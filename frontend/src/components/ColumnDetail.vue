<template>
  <div class="container">
    <div id="details-panel" v-if="column !== null" class="row panel">
      <div class="col">
        <h3>Datatype Selection</h3>
        <select id="type-input" class="form-select" aria-label="Choose a data type" :value="columnContext.parser" @change="selectDatatype">
          <option
            v-for="(availableType, functionName) in state.context.availableTypes"
            :value="functionName"
            :key="functionName"
            v-text="availableType.name">
          </option>
        </select>
        <div class="lead my-2" v-text="state.context.availableTypes[columnContext.parser].doc"></div>
        <div>
          <button class="btn btn-secondary" @click="appendSourceToEditor">Send code to editor</button>
        </div>
      </div>

      <div class="col">
        <DummyColumn
          :isSelected="column === state.context.selectedColumn"
          :header="columnContext.header"
          :entries="columnContext.entries"
          :width="'auto'"
          :color="state.context.availableTypes[columnContext.parser].color"
          :isEditable="true"
          :send="column.ref.send"
        ></DummyColumn>
      </div>

      <div id="column-feedback-panel" class="col">
        <h3>Clog Detection</h3>
        <div v-if="columnContext.errorsCount > 0">
          <div>The plumber found {{ columnContext.errorsCount }} problems:</div>
          <table class="table">
            <tr>
              <th scope="col">Entry</th>
              <th scope="col">Appearances</th>
              <th scope="col">Message</th>
            </tr>
            <tr v-for="clog in columnContext.parserErrors" :key="clog.row">
              <td v-text="clog.entry"></td>
              <td v-if="clog.count === 1" v-text="`row #${clog.row}`"></td>
              <td v-else v-text="`row #${clog.row} + ${clog.count - 1} more`"></td>
              <td v-text="clog.message"></td>
            </tr>
          </table>
        </div>
        <div v-else>
          <div>This column passes all checks</div>
        </div>
      </div>
    </div>
    <div v-else>No column selected</div>
  </div>
</template>


<script setup>
import {computed, defineProps} from 'vue';
import DummyColumn from './DummyColumn.vue';
import {getSelectedColumn} from "@/machines/main";

const props = defineProps({
  state: Object,
  send: Function,
});

const column = computed(() => getSelectedColumn(props.state))
const columnContext = computed(() => column.value.ref.state.context)

const selectDatatype = (event) => {
  column.value.ref.send({
    type: "SET_PARSER",
    parser: event.target.value,
  })
};

const appendSourceToEditor = () => {
  props.send({
    type: "APPEND_SOURCE",
    parser: columnContext.value.parser
  })
};

</script>
