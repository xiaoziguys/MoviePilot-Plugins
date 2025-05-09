<script setup>
import { ref } from 'vue'
import { search } from '../api/api.js'

const props = defineProps({
  api: {
    type: [Object, Function],
    required: true,
  },
  initialConfig: {
    type: Object,
    default: () => ({}),
  }
});

// 自定义事件，用于通知主应用刷新数据
const emit = defineEmits(['action', 'switch', 'close'])

// 搜索框相关数据和函数
const searchQuery = ref('')
const list = ref([]) // 声明list变量
const loading = ref(false) // 添加loading状态变量
const snackbar = ref(false) // 控制snackbar显示
const snackbarText = ref('') // snackbar文本
const pluginId = 'Site6VSupport'

// 目录选择对话框相关数据
const showDirectoryDialog = ref(false); // 控制目录选择对话框显示
const transferDirectories = ref([]); // 文件整理目录列表
const selectedDirectory = ref(null); // 用户选择的下载目录
const currentMagnetLink = ref(''); // 当前点击的磁力链接
const directoryLoading = ref(false); // 获取目录列表的loading状态
const magnetLoading = ref(false); // 磁力下载的loading状态

function performSearch() {
  console.log('执行搜索hahah:', searchQuery.value)
  if (!searchQuery.value) {
    return
  }
  loading.value = true // 开始加载
  props.api.get(`plugin/${pluginId}/search_from_6v`, {
    params: {
      query: searchQuery.value
    }
  }).then(data => {
    console.log('搜索结果:', data)
    list.value = data // 将搜索结果赋值给list
    // 处理搜索结果
  }).catch(error => {
    console.error('搜索失败:', error)
  }).finally(() => {
    loading.value = false // 结束加载
  })
}

function copyUrl(url) {
  navigator.clipboard.writeText(url).then(() => {
    console.log('URL copied to clipboard:', url);
    snackbarText.value = '链接已复制！';
    snackbar.value = true;
  }).catch(err => {
    console.error('Failed to copy URL:', err);
    snackbarText.value = '复制失败！';
    snackbar.value = true;
  });
}

// 打开目录选择对话框
function openDirectoryDialog(magnetLink) {
  currentMagnetLink.value = magnetLink;
  directoryLoading.value = true;
  props.api.get(`plugin/${pluginId}/get_transfer_directories`)
    .then(data => {
      transferDirectories.value = data;
      showDirectoryDialog.value = true;
    })
    .catch(error => {
      console.error('获取文件整理目录失败:', error);
      snackbarText.value = '获取下载目录失败！';
      snackbar.value = true;
    })
    .finally(() => {
      directoryLoading.value = false;
    });
}

// 执行磁力下载并带上选择的目录
function performMagnetDownloadWithDirectory() {
  if (!selectedDirectory.value || !currentMagnetLink.value) {
    snackbarText.value = '请选择下载目录并确保磁力链接有效！';
    snackbar.value = true;
    return;
  }

  magnetLoading.value = true;
  // 查找当前磁力链接对应的项目
  const currentItem = list.value.find(item => item.url === currentMagnetLink.value);
  props.api.post(`plugin/${pluginId}/add_magnet_download`, {
    magnet_link: currentMagnetLink.value,
    download_dir: selectedDirectory.value, // 添加下载目录参数
    title: currentItem ? currentItem.title : '', // 传递标题
    des: currentItem ? currentItem.des : '' // 传递描述
  })
  .then(response => {
    console.log('磁力下载结果:', response);
    snackbarText.value = response.message;
    snackbar.value = true;
    closeDirectoryDialog(); // 关闭对话框
  })
  .catch(error => {
    console.error('磁力下载失败:', error);
    snackbarText.value = '磁力下载失败！';
    snackbar.value = true;
  })
  .finally(() => {
    magnetLoading.value = false;
  });
}

// 关闭目录选择对话框
function closeDirectoryDialog() {
  showDirectoryDialog.value = false;
  selectedDirectory.value = null;
  currentMagnetLink.value = '';
}
</script>

<template>
  <div class="plugin-page" fluid>
    <!-- 搜索框和搜索按钮 -->
      <v-card flat class="rounded border">
        <!-- 标题区域 -->
        <v-card-title class="text-subtitle-1 d-flex align-center px-3 py-2 bg-primary-lighten-5">
          <v-icon icon="mdi-web" class="mr-2" color="primary" size="small" />
          <span>6v站点资源</span>
        </v-card-title>
        <v-card-text class="pt-4">
          <!-- 搜索框和搜索按钮 -->
          <v-row class="tool-bar">
            <v-col cols="5">
              <v-text-field
                v-model="searchQuery"
                label="搜索"
                variant="outlined"
                class="search-field"
              ></v-text-field>
            </v-col>
            <v-col cols="2">
              <v-btn @click="performSearch" class="search-btn mt-10px" :loading="loading">搜索</v-btn>
            </v-col>
          </v-row>
        <v-table
          height="500px"
          fixed-header
          class="rounded border"
        >
          <thead>
            <tr>
              <th class="text-left">
                标题
              </th>
              <th class="text-left">
                种子
              </th>
              <th class="text-right action-column">
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in list"
              :key="item.url"
            >
              <td>{{ item.title }}</td>
              <td>{{ item.des }}</td>
              <td class="action-column">
                <v-btn
                  density="comfortable"
                  icon
                  variant="text"
                  size="small"
                  color="white"
                  class="mr-1"
                  @click="openDirectoryDialog(item.url)" # 修改下载按钮的点击事件
                >
                  <v-icon icon="mdi-download" size="small"></v-icon>
                  <v-tooltip activator="parent" location="top">下载</v-tooltip>
                </v-btn>
                <v-btn
                  density="comfortable"
                  icon
                  variant="text"
                  color="white"
                  size="small"
                  @click="copyUrl(item.url)"
                >
                  <v-icon icon="mdi-content-copy" size="small"></v-icon>
                  <v-tooltip activator="parent" location="top">复制链接</v-tooltip>
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
    </v-card-text>
  </v-card>
  </div>
  <v-snackbar
    v-model="snackbar"
    :timeout="2000"
  >
    {{ snackbarText }}
  </v-snackbar>

  <!-- 目录选择对话框 -->
  <v-dialog v-model="showDirectoryDialog" persistent max-width="400">
    <v-card>
      <v-card-title class="text-h5">选择下载目录</v-card-title>
      <v-card-text>
        <v-select
          v-model="selectedDirectory"
          :items="transferDirectories"
          item-title="name"
          item-value="path"
          label="下载目录"
          variant="outlined"
          :loading="directoryLoading"
          :disabled="directoryLoading"
        ></v-select>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="closeDirectoryDialog">
          取消
        </v-btn>
        <v-btn color="blue-darken-1" variant="text" @click="performMagnetDownloadWithDirectory" :disabled="!selectedDirectory || magnetLoading" :loading="magnetLoading">
          确定
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.plugin-page {
  padding: 10px;
}
.bg-primary-lighten-5 {
  background-color: rgba(var(--v-theme-primary), 0.07);
}

.tool-bar {
  margin-bottom: 10px;
}
.mt-10px {
  margin-top: 10px;
}
.action-column {
  width: 80px; /* Adjust as needed */
}

.search-btn ::v-deep(.v-btn__loader) {
  color: white;
}
</style>