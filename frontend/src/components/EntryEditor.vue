<template>
  <div class="row">
    <div class="col-md">
      <div class="card" style="width: 18rem;">
        <div class="card-body">
          <h5 class="card-title">Card title</h5>
          <p class="card-text">{{ currentEntry }}</p>
        </div>
      </div>
    </div>
    <div class="col-md">
      <button class="btn btn-secondary" @click="move(-1)" :disabled="currentIndex === 0">Previous</button>
      <button class="btn btn-primary" @click="move(1)" :disabled="currentIndex === exceptions.length - 1">Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps } from 'vue';

const props = defineProps({
  exceptions: Array,
});
const exceptions = props.exceptions || ["Default Entry 1", "Default Entry 2"];
const currentIndex = ref(0);

const currentEntry = computed(() => exceptions[currentIndex.value]);

const move = (direction) => {
  currentIndex.value += direction;
};
</script>
