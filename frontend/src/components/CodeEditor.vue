<template>
  <h4>Data Types</h4>
  <div class="container">
    <div id="types-panel" class="row panel">
      <div>
        <button
          class="btn btn-lg btn-primary mb-4"
          @click="appendCodeToJournal"
        >
          Run python and update definitions
        </button>
      </div>
      <div class="col col-lg-12 python-code">
        <Codemirror
          :model-value="state.context.code"
          :options="{ mode: 'python', lineNumbers: false }"
          :extensions="extensions"
          @change="updateCode"
        />
        <pre id="errors" v-if="state.context.pythonError" class="my-4">{{ state.context.pythonError }}</pre>
      </div>
    </div>
    <div :value="state.context.code">
    </div>
  </div>
</template>

<script setup>
import { Codemirror } from 'vue-codemirror'
import { python } from "@codemirror/lang-python";
import {defineProps} from 'vue'

const props = defineProps({
  state: Object,
  send: Function,
});

const extensions = [python()]

function updateCode(code) {
  props.send({ type: 'EDIT_CODE', code });
}

const appendCodeToJournal = async () => {
  props.send("APPEND_CODE_TO_JOURNAL")
}
</script>

<style scoped>

.python-code {
  background-color: white;
}

</style>
