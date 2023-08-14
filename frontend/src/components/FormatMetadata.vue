<template>
  <section id="metadata-section">
    <div class="row">
      <div class="col-md">
        <input type="file" class="form-control form-control-lg mb-4" @change="handleFileChange" :disabled="!state.matches('running')">
      </div>
      <div class="col-md lead" v-text="statusMessage"></div>
    </div>
    <form action="javascript:void(0)" id="plumber-form">
      <input type="hidden" name="xstate_json" :value="JSON.stringify(state)">
      <div class="row">
        <div class="col-md">
          <input id="format-name" type="text" name="name" class="form-control form-control-lg mb-4" placeholder="Format name">
        </div>
        <div class="col-md">
          <button class="btn btn-primary btn-lg form-control" @click="publish" :disabled="state.context.publishRequested">Publish</button>
        </div>
        <div class="col-md" v-if="state.context.checkURL">
          <a :href="state.context.checkURL" class="btn btn-primary btn-lg">View Published Checker</a>
        </div>
      </div>
      <textarea id="format-description" name="description" class="form-control form-control-lg mb-4" placeholder="Describe the format..."></textarea>
    </form>
  </section>
</template>

<script setup>
import { defineProps, computed } from 'vue';
const props = defineProps(['state', 'send']);

const statusMessage = computed(() => {
  if (props.state.matches('pageLoading')) {
    return 'Loading...';
  }
  if (props.state.matches('pyodideLoading')) {
    return 'Loading Python runtime...';
  }
  if (props.state.matches('running')) {
    return 'Python ready.';
  }
  return '';
});

function handleFileChange(event) {
  const file = event.target.files[0];
  props.send('FILE_INPUT', { file });
}

function publish() {
  props.send('PREP_FOR_PUBLISH')
}

</script>

<style scoped>

</style>
