import {createMachine, assign } from 'xstate';

export const pyodideWorker = new Worker(`/static/main/webworker.js?${Date.now()}`);

export const pyodideMachine = createMachine({
  id: "pyodide",
  preserveActionOrder: true,
  context: {
    jobQueue: [],
    error: null,
    main: null,
  },
  initial: "loading",
  states: {
    loading: {
      entry: () => pyodideWorker.postMessage({ type: "loadPyodide" }),
      type: "parallel",
      states: {
        waitForPyodide: {
          initial: "waiting",
          states: {
            waiting: {
              on: {
                JOB_COMPLETED: "done"
              }
            },
            done: {
              type: "final"
            }
          }
        },
        waitForMain: {
          initial: "waiting",
          states: {
            waiting: {
              on: {
                MAIN_REFERENCE: { // TODO we don't want to run this for the verify page?
                  actions: assign({
                    main: (context, event) => event.data
                  }),
                  target: 'done'
                }
              }
            },
            done: {
              type: "final"
            }
          }
        }
      },
      onDone: {
        actions:  (context) => context.main.send("PYODIDE_READY"),
        target: 'running'
      }
    },
    running: {
      on: {
        SUBMIT_JOB: {
          actions: ['queueJob'],
          internal: true,
        },
        JOB_COMPLETED: {
          actions: [
            (context, event) => {
              const transitionType = (context.jobQueue[0] && context.jobQueue[0].transition) || "PYODIDE_JOB_COMPLETED";
              context.main.send({
                type: transitionType,
                jobInfo: context.jobQueue[0].jobInfo,
                data: JSON.parse(event.data.result),
              });
            },
            'removeJob',
            'processJob',
          ],
          target: 'running',
        },
        '*': {
          actions: (context, event) => {
            console.log('Unhandled event received:', event);
          }
        }
      },
    },
  },
}, {
  actions: {
    processJob: (context) => {
      if (context.jobQueue.length > 0) {
        const job = context.jobQueue[0];
        pyodideWorker.postMessage(job);
      }
    },
    queueJob: assign({
      jobQueue: (context, event) => {
        if(context.jobQueue.length === 0) {
          pyodideWorker.postMessage(event.data);
          return [event.data]
        } else {
          return [...context.jobQueue, event.data]
        }
      },
    }),
    removeJob: assign({
      jobQueue: (context) => context.jobQueue.slice(1)
    }),
  },
});
