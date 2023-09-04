<template>
  <section id="metadata-section">
    <div class="row">
      <div class="col-md">
        <input type="file" class="form-control form-control-lg mb-4" @change="handleFileChange" :disabled="!state.matches('running')">
      </div>
      <div class="col-md lead" v-text="statusMessage"></div>
    </div>
    <div>{{ parserResults }}</div>
    <div v-if="parserResults">
      <EntryEditor
        :exceptions="parserResults.exceptions"
      />
    </div>
  </section>
</template>

<script setup>
import { useMachine } from '@xstate/vue';
import {pyodideMachine, pyodideWorker} from "@/machines/pyodide";
import {onMounted, onUnmounted, computed, ref} from "vue";
import {interpret} from "xstate";
import {checkerMachine} from "@/machines/checker";
import EntryEditor from "@/components/EntryEditor.vue";

const machine = useMachine(checkerMachine);
const { send, state } = machine;

const stateRef = ref(state)

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

const statusMessage = computed(() => {
  if (stateRef.value.matches('pageLoading')) {
    return 'Loading...';
  }
  if (stateRef.value.matches('pyodideLoading')) {
    return 'Loading...';
  }
  if (stateRef.value.matches('running')) {
    return 'Plumber ready.';
  }
  return '';
});

const parserResults = computed(() => {
  if(stateRef.value.context) {
    return stateRef.value.context.parserResults
  }
  return ""
})

function handleFileChange(event) {
  const file = event.target.files[0];
  send('FILE_INPUT', { file });
}

</script>

<style scoped>

</style>