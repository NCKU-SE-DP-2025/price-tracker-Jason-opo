<template>
    <div class="wrapper">
        <h1>各類商品物價概覽</h1>
        <h3 v-if="!isLoading" class="subtitle">資料更新時間：{{updateTime}}</h3>
        <div class="prices">
            <CategoryPrice class="category" v-for="category in categoryList" :key="category"
                :category="category" :isLoading="isLoading" :errorMessage="errorMessage" :priceData="getPriceData(category)"></CategoryPrice>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import CategoryPrice from '@/components/CategoryPrice.vue';
import Categories from '@/constants/categories';
import { usePricesStore } from '@/stores/prices';

// Store
const store = usePricesStore();

// 狀態
const prices = ref({});

// 元件掛載時取得資料
onMounted(() => {
  store.fetchPrices();
});

// 計算屬性：分類清單
const categoryList = computed(() => Object.keys(Categories));

// 計算屬性：載入狀態
const isLoading = computed(() => store.isLoading);

// 計算屬性：錯誤訊息
const errorMessage = computed(() => store.errorMessage);

// 計算屬性：更新時間
const updateTime = computed(() => store.updatedTime);

// 方法：取得分類資料
function getPriceData(category) {
  return store.getPricesByCategory(category);
}
</script>

<style scoped>
.wrapper{
    padding: 3em 5em;
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    height: calc(100% - 4.5em);
    box-sizing: border-box;
}
.prices{
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
}
.category{
    margin: 1em;
    flex-grow: 1;
}
.subtitle{
    font-weight: normal;
    margin-top: .5em;
}
</style>