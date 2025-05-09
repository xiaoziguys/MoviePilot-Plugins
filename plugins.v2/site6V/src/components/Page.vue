<script setup>
import { ref } from 'vue'
import { search } from '../api/api.js'

// 自定义事件，用于通知主应用刷新数据
const emit = defineEmits(['action', 'switch', 'close'])

// 搜索框相关数据和函数
const searchQuery = ref('')

function performSearch() {
  console.log('执行搜索:', searchQuery.value)
  if (!searchQuery.value) {
    return
  }
  search(searchQuery.value)
}

// 接收API对象
const props = defineProps({
  api: {
    default: () => {}
  }
})
</script>

<template>
  <v-container class="plugin-page" fluid>
    <!-- 搜索框和搜索按钮 -->
    <v-row>
      <v-col cols="10">
        <v-text-field
          v-model="searchQuery"
          label="搜索"
          prepend-icon="mdi-magnify"
          variant="outlined"
          class="search-field"
        ></v-text-field>
      </v-col>
      <v-col cols="2">
        <v-btn @click="performSearch" class="search-btn" height="56" width="100">搜索</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>