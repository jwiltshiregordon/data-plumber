<template>
  <div class="row">
    <div class="col-md">
      <div class="card" style="width: 18rem;">
        <div class="card-body">
          <h5 class="card-title">{{ currentEntry[2] }}</h5>
          <p class="card-text">row: {{ currentEntry[0] }} column: {{ currentEntry[1] }}</p>
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

const currentIndex = ref(0);
const currentEntry = computed(() => props.exceptions[currentIndex.value]);

const move = (direction) => {
  currentIndex.value += direction;
};
</script>
