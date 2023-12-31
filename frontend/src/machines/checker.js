import { createMachine, assign } from 'xstate';

export const checkerMachine = createMachine({
  id: 'main',
  preserveActionOrder: true,
  initial: 'pageLoading',
  context: {
    pyodide: null,
    fileURLs: null,
    example: null,
    parserResults: "",
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
        FILE_INPUT: {
          actions: assign({example: (context, event) => event.file}),
          target: "loadingExample"
        },
        PARSED_EXAMPLE: {
          actions: [
            assign({
              parserResults: (context, event) => event.data
            })
          ]
        }
      }
    },
    loadingExample: {
      invoke: {
        id: "loadingExampleData",
        src: sendExampleToPyodide,
        onDone: {
          actions: (context) => context.pyodide.send({type: "SUBMIT_JOB", data: {type: "python", python: "from parser import parse_csv_file\nimport json\nfrom dataclasses import asdict\ndata, exceptions = parse_csv_file('example.csv')\nrows = [asdict(row) for row in data]\njson.dumps(dict(rows=rows, exceptions=exceptions))", transition: "PARSED_EXAMPLE", jobInfo: {} }}),
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
