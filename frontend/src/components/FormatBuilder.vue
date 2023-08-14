<template>
  <main>
    <FormatMetadata :state="state" :send="send" />
    <div v-if="state.matches('running')">
      <section id="columns-section">
        <h4>Add, Remove, or Select Columns</h4>
        <ColumnsDisplay
          :columns="state.context.columns"
          :selectedIndex="state.context.selectedColumnIndex"
          :availableTypes="state.context.availableTypes"
          :send="send"
          :state="state"
        />
      </section>

      <section
        id="details-section"
        v-if="state.context.selectedColumnIndex !== -1"
      >
        <h4>Edit Column "{{getSelectedColumn(state).ref.state.context.header}}"</h4>
        <ColumnDetail :state="state" :send="send"/>
      </section>

      <section v-else>
        <h4>No Column Selected</h4>
      </section>

      <section id="custom-types">
        <CodeEditor :state="state" :send="send" />
      </section>

      <section>
        <h4>Generated Parser</h4>
        <div class="container">
          <div id="generated-code-panel" class="row panel">
            <div>
              <button class="btn btn-lg btn-primary mb-4 mx-4" @click="getParser">
                Update parser code
              </button>
              <button class="btn btn-lg btn-primary mb-4" @click="copyGeneratedCode(state.context.generatedParser)">
                Copy parser code to clipboard
              </button>
            </div>
            <div class="col col-lg-12">
              <textarea id="generated-code" name="generated-code" :value="state.context.generatedParser"></textarea>
            </div>
          </div>
        </div>
      </section>
    </div>
    <section v-else>
      <h4>Loading python runtime...</h4>
    </section>

  </main>
</template>

<script setup>
import { useMachine } from '@xstate/vue';
import {pyodideMachine, pyodideWorker} from "@/machines/pyodide";
import {getSelectedColumn, mainMachine } from '@/machines/main';
import ColumnsDisplay from "@/components/ColumnsDisplay.vue";
import ColumnDetail from "@/components/ColumnDetail.vue";
import FormatMetadata from "@/components/FormatMetadata.vue";
import CodeEditor from "@/components/CodeEditor.vue";
import {onMounted, onUnmounted } from "vue";
import {interpret} from "xstate";

const machine = useMachine(mainMachine);
const { send, state } = machine;

const pyodide = interpret(pyodideMachine);
pyodide.start();


machine.service.subscribe((state) => {
  console.log([
    "main",
    state,
    `transition: ${state.event.type}`,
    `state: ${state.toStrings().join(' / ')}`
  ]);
})

pyodide.subscribe((state) => {
  console.log([
    "pyodide",
    state,
    `transition: ${state.event.type}`,
    `state: ${state.toStrings().join(' / ')}`
  ]);
})

pyodide.send({
  type: "MAIN_REFERENCE",
  data: machine.service,
})

pyodideWorker.onmessage = (e) => {
  if (e.data.result !== undefined && e.data.result.pyodideLoaded) {
    pyodide.send('JOB_COMPLETED');
  } else {
    pyodide.send({type: 'JOB_COMPLETED', data: e.data });
  }
}

const handleLoad = () => {
  send({type: 'PAGE_LOADED', fileURLs: window.fileURLs, pyodide: pyodide});
};

onMounted(() => {
  if (document.readyState === "complete") {
    handleLoad();
  } else {
    window.addEventListener('load', handleLoad);
  }
});

onUnmounted(() => {
  window.removeEventListener('load', handleLoad);
});

const getParser = () => {
  send("UPDATE_GENERATED_PARSER")
}
const copyGeneratedCode = (code) => {
  navigator.clipboard.writeText(code)
  .then(() => {
    console.log('Copied to clipboard');
  })
  .catch(err => {
    console.error('Could not copy text: ', err);
  });
}
</script>
