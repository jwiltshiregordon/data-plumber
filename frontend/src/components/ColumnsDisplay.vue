<template>
  <div ref="columnsPanelRef" id="columns-panel" class="panel" tabindex="0" @keydown="handleKeyDown">
    <DummyColumn
      v-for="(column, columnIndex) in columnContexts"
      :key="columnIndex"
      :isSelected="columnIndex === selectedIndex"
      :header="column.header"
      :entries="column.entries"
      :width="columnWidth"
      :color="availableTypes[column.parser].color"
      :isEditable="false"
      @select="selectColumn(column.id)"
      @remove="removeColumn(column.id)"
    ></DummyColumn>
    <div class="dummy-column new-column" :style="getNewColumnStyle" @click="addColumn">
      <div class="dummy-column-header no-edit">
        <span id="new-column-header">New Column</span>
      </div>
      <div class="column-plus no-edit"><div>+</div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, onMounted, onUpdated } from 'vue';
import DummyColumn from './DummyColumn.vue';

const props = defineProps({
  columns: Array,
  selectedIndex: Number,
  availableTypes: Object,
  send: Function,
  state: Object,
});

const columnContexts = computed(() => props.state.context.columns.map((column) => column.ref.state.context))
const columnsPanelRef = ref(null);

const longestHeaderLength = () => {
  if (props.columns.length > 0) {
    return Math.max(...props.columns.map(column => column.ref.state.context.header.length), 10);
  }
  return 10;
};

// Compute max header length when component is mounted
onMounted(() => {
  scrollIntoView();
});

const selectColumn = (columnId) => {
  props.send('SELECT_COLUMN', { columnId });
  scrollIntoView();
};

const removeColumn = (columnId) => {
  props.send('REMOVE_COLUMN', { columnId });
};

const addColumn = () => {
  props.send('ADD_COLUMN');
};

const calculateColumnWidth = () => {
  const charWidth = 9;
  const maxWidth = longestHeaderLength();
  return `${(maxWidth + 1) * charWidth + 50}px`;
};

const columnWidth = computed(() => {
  return calculateColumnWidth();
});

const getNewColumnStyle = computed(() => {
  return {
    width: calculateColumnWidth(),
    backgroundColor: 'white',
  };
});

const handleKeyDown = (event) => {
  if (event.key === 'ArrowLeft') {
    props.send('SELECT_COLUMN', { index: props.state.context.selectedColumnIndex - 1 });
    scrollIntoView();
  } else if (event.key === 'ArrowRight') {
    props.send('SELECT_COLUMN', { index: props.state.context.selectedColumnIndex + 1 });
    scrollIntoView();
  }
};

const scrollIntoView = () => {
  const panelElement = columnsPanelRef.value;
  const selectedColumnElement = panelElement.querySelector('.dummy-column-selected');

  if (selectedColumnElement) {
    const panelRect = panelElement.getBoundingClientRect();
    const selectedColumnRect = selectedColumnElement.getBoundingClientRect();

    if (selectedColumnRect.left < panelRect.left) {
      const scrollAmount = panelRect.left - selectedColumnRect.left;
      panelElement.scrollTo({
        left: panelElement.scrollLeft - scrollAmount,
        behavior: 'smooth'
      });
    } else if (selectedColumnRect.right > panelRect.right) {
      const scrollAmount = selectedColumnRect.right - panelRect.right;
      panelElement.scrollTo({
        left: panelElement.scrollLeft + scrollAmount,
        behavior: 'smooth'
      });
    }
  }
};

onUpdated(scrollIntoView);
</script>
