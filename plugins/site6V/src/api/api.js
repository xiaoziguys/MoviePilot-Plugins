import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: 'https://www.66s6.net/e', // 假设 API 基础路径是 /api，您可以根据实际情况调整
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'tinmklastsearchtime=1733461568'
  },
  withCredentials: true // 确保cookie被发送
})

const payload = {
  show: 'title',
  tempid: 1,
  tbname: 'article',
  mid: 1,
  dopost: 'search',
  submit: '',
  keyboard: ''
};

const formBody = new URLSearchParams();
    for (const key in payload) {
        formBody.append(key, payload[key].toString());
    }

// 搜索 API 方法
export function search(query) {
  formBody.set('keyboard', query)
  return apiClient.post(
    '/search/1index.php', {
    body: formBody.toString()
  })
}

export default apiClient