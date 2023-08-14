import {createMachine, assign, sendParent} from 'xstate';

export const columnMachine = createMachine({
  id: 'column',
  preserveActionOrder: true,
  initial: 'starting',
  context: {
    id: null,
    header: null,
    parser: null,
    entries: [],
    parserErrors: null,
    errorsCount: null,
    exampleColumnIndex: null,
  },
  states: {
    starting: {
      on: {
        INITIALIZE: {
          actions: assign({
            id: (context, event) => event.data.id,
            header: (context, event) => event.data.header || "New Column",
            parser: (context, event) => event.data.datatype || "string_parser",
            entries: (context, event) => event.data.entries || [],
            parserErrors: (context, event) => event.data.parserErrors || [],
            errorsCount: (context, event) => event.data.errorsCount || 0,
            exampleColumnIndex: (context, event) => (event.data.exampleColumnIndex === undefined) ? null : event.data.exampleColumnIndex,
          }),
          target: "idle"
        }
      }
    },
    idle: {
      on: {
        SET_HEADER: {
          actions: assign({ header: (_, event) => event.header })
        },
        SET_PARSER: {
          actions: [
            assign({ parser: (_, event) => event.parser }),
            sendParent((context) => ({
              type: "PARSE_REQUEST",
              columnId: context.id,
              parser: context.parser,
              exampleColumnIndex: context.exampleColumnIndex,
            }))
          ],
        },
        PARSER_RESPONSE: {
          actions: assign({
            parserErrors: (context, event) => event.result.exceptions,
            errorsCount: (context, event) => event.result.count,
          })
        }
      }
    },
  }
});
