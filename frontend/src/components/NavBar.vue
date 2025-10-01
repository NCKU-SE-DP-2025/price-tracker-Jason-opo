<template>
  <nav class="navbar">
    <div class="navbar-header">
      <div class="title">
        <RouterLink to="/overview">價格追蹤小幫手</RouterLink>
      </div>

      <!-- 漢堡按鈕（手機才顯示） -->
      <button
        class="menu-toggle"
        type="button"
        @click="toggleMenu"
        aria-controls="main-menu"
        :aria-expanded="showMenu.toString()"
        aria-label="切換選單"
      >
        ☰
      </button>
    </div>

    <!-- 導覽選單：桌機常駐、手機用 .show 切換 -->
    <ul id="main-menu" class="options" v-if="isMenuOpen">
      <li><RouterLink to="/overview">物價概覽</RouterLink></li>
      <li><RouterLink to="/trending">物價趨勢</RouterLink></li>
      <li><RouterLink to="/news">相關新聞</RouterLink></li>
      <li v-if="!isLoggedIn"><RouterLink to="/login">登入</RouterLink></li>
      <li v-else @click="logout">Hi, {{ getUserName }}! 登出</li>
    </ul>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'

const userStore = useAuthStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)
const getUserName = computed(() => userStore.getUserName)
const isMenuOpen = ref(true)
const isMobile = ref(window.matchMedia("(max-width: 768px)").matches);

// 手機預設收起
const showMenu = ref(false)

let mq;
function checkMobile(match){
  isMobile.value = match.matches;
  if(!isMobile.value) isMenuOpen.value = true;
  else isMenuOpen.value = false;
}



function logout() {
  userStore.logout()
  showMenu.value = false // 手機使用上較直覺：登出後順便收起
}



function toggleMenu() {
  if(isMobile.value) isMenuOpen.value = !isMenuOpen.value;
}

// Esc 關閉（僅手機情境有意義，但無妨）
function onKeydown(e) {
  if (e.key === 'Escape') showMenu.value = false
}

// 路由切換時自動關閉（避免在手機上保持展開）
const route = useRoute()
watch(
  () => route.fullPath,
  () => { showMenu.value = false }
)

onMounted(() => {
  isMenuOpen.value = !isMobile.value ? true : false;
  mq = window.matchMedia("(max-width: 768px)");
  mq.addEventListener('change', checkMobile);
  document.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  mq.removeEventListener('change', checkMobile);
})
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  background-color: #f3f3f3;
  width: 100%;
  align-items: center;
  box-shadow: 0 0 5px #757575ff;
}

.navbar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5em;
  height: 4.5em;
  width: 100%;
}

/* 桌機：選單常駐橫排 */
.navbar ul {
  list-style: none;
  display: flex;
  justify-content: space-around;
  margin: 0;
  padding: 0 1rem 0 0;
}

.title > a {
  font-size: 1.4em;
  font-weight: bold;
  color: #2c3e50 !important;
  text-decoration: none;
}

.navbar li {
  color: #575B5D;
  margin: 0 .5em;
  font-size: 1.2em;
  white-space: nowrap;
}

.navbar li:hover{
  cursor: pointer;
  font-weight: bold;
}

.navbar a {
  text-decoration: none;
  color: #575B5D;
}

/* 漢堡按鈕，手機版才會顯示 */
.menu-toggle {
  display: none;
  font-size: 24px;
  cursor: pointer;
  border: 1px solid #d0d0d0;
  background: #fff;
  border-radius: 8px;
  padding: 6px 10px;
}

/* ---------- 手機版 ---------- */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column; /* 讓 ul 能排在 header 下方 */
  }

  .navbar-header {
    width: 100%;
  }

  .menu-toggle {
    display: flex;            /* 手機顯示漢堡 */
    justify-content: center;
    align-items: center;
    font-size: 1.5em;
  }

  /* 手機：選單改為直向、預設隱藏，按鈕展開 */
  .options {
    display: none;
    flex-direction: column;
    width: 100%;
    padding: 0;
  }


.options.show {
  display: flex !important;
}


  .options li {
    text-align: center;
    padding: 10px 0;
    margin-left: 0;
    border-top: 1px solid #ccc;
    width: 100%;
    box-sizing: border-box;
  }
}
</style>