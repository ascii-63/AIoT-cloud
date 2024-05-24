<template>
  <div id="app">
    <div class="container">
      <div class="left">
        <h2>Logs</h2>
        <ul>
          <li v-for="log in logs" :key="log.id">{{ log.message }}
            <button @click="fetchImage(log.url)">View Image</button>
          </li>
        </ul>
      </div>
      <div class="right">
        <h2>Image</h2>
        <img :src="imageUrl" v-if="imageUrl" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      logs: [],
      imageUrl: ''
    }
  },
  created() {
    this.fetchLogs();
    setInterval(this.fetchLogs, 5000); // Poll every 5 seconds
  },
  methods: {
    fetchLogs() {
      axios.get('http://localhost:5000/logs')
        .then(response => {
          this.logs = response.data;
        })
        .catch(error => {
          console.error("There was an error fetching the logs!", error);
        });
    },
    fetchImage(url) {
      axios.get(`http://localhost:5000/image`, { responseType: 'blob' })
        .then(response => {
          const url = URL.createObjectURL(response.data);
          this.imageUrl = url;
        })
        .catch(error => {
          console.error("There was an error fetching the image!", error);
        });
    }
  }
}
</script>

<style>
.container {
  display: flex;
}

.left,
.right {
  width: 50%;
  padding: 20px;
}
</style>
