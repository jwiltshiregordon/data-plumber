import { createMachine, assign, spawn } from 'xstate';
import { columnMachine } from "@/machines/column";
import {v4 as uuidv4} from "uuid";


const addColumnAction = assign({
  columns: (context) => {
    const child = spawn(columnMachine, { sync: true });
    const id = uuidv4();
    child.send({
      type: "INITIALIZE",
      data: { id }
    });
    return [...context.columns, { id: id, ref: child }];
  }
});

const addExampleColumnsAction = assign({
  columns: (context, event) => {
    let columns = [...context.columns]
    for(const column of event.data.result.columns) {
      const child = spawn(columnMachine, { sync: true });
      const id = uuidv4();
      child.send({
        type: "INITIALIZE",
        data: {...column, id }
      });
      columns.push({id, ref: child})
    }
    return columns
  }
})

export const mainMachine = createMachine({
  id: 'main',
  preserveActionOrder: true,
  initial: 'pageLoading',
  context: {
    columns: [],  //  { id: columnId, ref: columnMachineInstance }
    selectedColumnIndex: -1,
    pyodide: null,
    availableTypes: null,
    fileURLs: null,
    example: null,
    code: "",
    generatedParser: "",
    journal: "",
    publishRequested: false,
    checkURL: null,
  },
  states: {
    pageLoading: {
      on: {
        PAGE_LOADED: {
          actions: assign({
            fileURLs: (_, event) => event.fileURLs,
            pyodide: (_, event) => event.pyodide,
          }),
          target: 'pyodideLoading',
        }
      }
    },
    pyodideLoading: {
      initial: 'loadingMachine',
      states: {
        loadingMachine: {
          on: {
            PYODIDE_READY: {
              target: 'loadingFiles',
            }
          },
        },

        loadingFiles: {
          entry: (context) => context.pyodide.send({type: "SUBMIT_JOB", data: {type: "fetchFiles", fileURLs: context.fileURLs}}),
          on: {
            PYODIDE_JOB_COMPLETED: {
              target: 'augmentingSystemPath'
            },
          }
        },

        augmentingSystemPath: {
          entry: (context) => context.pyodide.send({type: "SUBMIT_JOB", data: {type: "python", python: "import sys\nsys.path.insert(0, '.')"}}),
          on: {
            PYODIDE_JOB_COMPLETED: {
              target: 'gettingAvailableTypes'
            }
          }
        },

        gettingAvailableTypes: {
          entry: (context) => context.pyodide.send(pythonJob("available_plumbers", "AVAILABLE_TYPES_CALCULATED")),
          on: {
            AVAILABLE_TYPES_CALCULATED: {
              actions: [
                assign({
                  availableTypes: (context, event) => event.data.result,
                })
              ],
              target: 'done'
            }
          }
        },

        done: {
          type: 'final'
        }
      },
      onDone: 'running',
    },
    running: {
      on: {
        ADD_COLUMN: {
          actions: addColumnAction
        },
        FILE_INPUT: {
          actions: assign({example: (context, event) => event.file}),
          target: "loadingExample"
        },
        REMOVE_COLUMN: {
          actions: assign({
            columns: (context, event) => context.columns.filter(column => column.id !== event.columnId)
          })
        },
        SELECT_COLUMN: {
          actions: assign({
            selectedColumnIndex: (context, event) => context.columns.findIndex(column => column.id === event.columnId)
          })
        },
        PARSE_REQUEST: {
          actions: (context, event) => requestParseColumn(context, event.parser, event.columnId)
        },
        COLUMN_PARSED: {
          actions: [
            (context, event) => {
              const column = context.columns.find((column) => column.id === event.jobInfo.columnId)
              if(column !== undefined) {
                column.ref.send({
                  type: "PARSER_RESPONSE",
                  result: event.data.result
                })
              }
            }
          ]
        },
        SUBMIT_JOB: {
          actions: (context) => context.pyodide.send((_, event) => event)
        },
        EXAMPLE_WRITTEN: {
          actions: (context) => context.pyodide.send(pythonJob("load_example_columns", "EXAMPLE_LOADED"))
        },
        EXAMPLE_LOADED: {
          actions: [
            assign({
              availableTypes: (context, event) => event.data.result.availableTypes
            }),
            addExampleColumnsAction
          ]
        },
        EDIT_CODE: {
          actions: assign({code: (context, event) => event.code })
        },
        APPEND_SOURCE: {
          actions: assign({code: (context, event) => {
              const sourceCode = context.availableTypes[event.parser].code
              return context.code + '\n' + sourceCode
            }
          })
        },
        APPEND_CODE_TO_JOURNAL: {
          actions: (context) => context.pyodide.send(pythonJob("append_code_to_journal", "JOURNAL_UPDATED", {python_code: context.code}))
        },
        JOURNAL_UPDATED: {
          actions: [
            (context, event) => {
              const updatedParsers = event.data.result;
              context.columns
                .filter(column => updatedParsers.includes(column.ref.state.context.parser))
                .map((column) => {
                  requestParseColumn(context, column.ref.state.context.parser, column.id)
                });
            },
            (context) => context.pyodide.send(pythonJob("available_plumbers", "AVAILABLE_TYPES_CALCULATED"))
          ],
        },
        AVAILABLE_TYPES_CALCULATED: {
          actions: assign({availableTypes: (context, event) => event.data.result})
        },
        UPDATE_GENERATED_PARSER: {
          actions: (context) => context.pyodide.send(pythonJob("render_parser", "PARSER_RENDERED", {columns: context.columns.map((column) => column.ref.state.context)}))
        },
        PARSER_RENDERED: {
          actions: assign({
            generatedParser: (context, event) => event.data.result
          })
        },
        PREP_FOR_PUBLISH: {
          actions: [
            (context) => context.pyodide.send(pythonJob("prep_for_publish", "READY_TO_PUBLISH", {columns: context.columns.map((column) => column.ref.state.context)})),
            assign({
              publishRequested: true,
            })
          ]
        },
        READY_TO_PUBLISH: {
          actions: assign({
            generatedParser: (context, event) => event.data.result.generated_parser,
            journal: (context, event) => event.data.result.journal,
          }),
          target: "publishing",
        }
      }
    },
    publishing: {
      invoke: {
        src: publish,
        onDone: {
          actions: assign({
            publishRequested: false,
            checkURL: (context, event) => event.data["check_url"],
          }),
          target: "running"
        }
      },
    },
    loadingExample: {
      invoke: {
        id: "loadingExampleData",
        src: sendExampleToPyodide,
        onDone: {
          target: "running"
        },
        onError: {
          actions: (context, event) => console.log(["error while working", event])
        }
      }
    },
    error: {
      type: 'final'
    }
  },
});

export function getSelectedColumn(state) {
  return state.context.columns[state.context.selectedColumnIndex] || null;
}

function pythonJob(funcname, transition, kwargs = {}, jobInfo = {}) {
  const python = `import main
kwargs = r"""${JSON.stringify(kwargs)}"""
main.${funcname}(kwargs)`;
  return {type: "SUBMIT_JOB", data: {type: "python", python: python, transition, jobInfo }}
}

async function readFile(context) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      resolve(event.target.result);
    };
    reader.onerror = (error) => {
      reject(error);
    };
    reader.readAsText(context.example);
  });
}

async function sendExampleToPyodide(context){
  const content = await readFile(context)
  const fileContents = [{ content, path: "example.csv"}]
  context.pyodide.send({type: "SUBMIT_JOB", data: {type: "writeFiles", fileContents, transition: "EXAMPLE_WRITTEN" }})
}

function requestParseColumn(context, parser, columnId) {
  const column = context.columns.find((column) => column.id === columnId)
  const exampleColumnIndex = column.ref.state.context.exampleColumnIndex;
  if(exampleColumnIndex === null) {
    return;
  }
  const kwargs = {
    column_plumber_function: parser,
    example_column_index: exampleColumnIndex,
  }
  context.pyodide.send(pythonJob("parse_example", "COLUMN_PARSED", kwargs, {columnId}))
}

async function publish(context) {
  return new Promise((resolve, reject) => {
    const formElement = document.querySelector('#plumber-form');
    const formData = new FormData(formElement);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);
    formData.append('generated_parser', context.generatedParser);
    fetch('/format-builder/', {
      method: 'POST',
      body: formData,
    })
      .then(response => {
        if (!response.ok) {
          reject(new Error(`HTTP error ${response.status}`));
        }
        return response.json();
      })
      .then(json => resolve(json))
      .catch(error => reject(error));
  });
}
