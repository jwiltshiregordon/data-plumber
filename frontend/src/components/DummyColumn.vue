<template>
  <div :class="dummyColumnClass" :style="getColumnStyle" @click="$emit('select')">
    <div class="dummy-column-header"
       :class="{ 'no-edit': !isEditable, 'dummy-column-header-edit': isEditable }"
       :contenteditable="isEditable"
       @blur="updateHeader"
       @keydown.enter.prevent="updateHeader"
    >
      <span ref="headerText" v-text="header"></span>
      <span class="remove-button" v-if="!isEditable" @click.stop="$emit('remove')" style="font-family: sans-serif">X&nbsp;</span>
    </div>
    <p class="mx-3 my-2" v-for="(entry, index) in entries" :key="index" v-text="entry"></p>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue';

const props = defineProps({
  isSelected: {
    type: Boolean,
    default: false,
  },
  header: {
    type: String,
    required: true,
  },
  entries: {
    type: Array,
    required: true,
  },
  width: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    required: true,
  },
  isEditable: {
    type: Boolean,
    default: false,
  },
  send: Function,
});

defineEmits(['select', 'remove']);

const dummyColumnClass = computed(() => {
  let classString = "dummy-column";
  if(props.isEditable) {
    classString += " dummy-column-detail"
    return classString;
  }
  if (props.isSelected) {
    classString += " dummy-column-selected";
  }
  return classString;
});

const getColumnStyle = computed(() => {
  return {
    width: props.width,
    backgroundColor: props.color,
  };
});

const updateHeader = (event) => {
  const header = event.target.innerText.trim();
  props.send('SET_HEADER', { header })
}
</script>
