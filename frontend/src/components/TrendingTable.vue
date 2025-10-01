<template>
    <div class="trending-table">
        <table>
            <thead>
                <tr>
                    <th rowspan="2">年份</th>
                    <th v-for="month in months" :key="month">{{ month }}</th>
                </tr>
            </thead>
            <tbody>
                <template v-for="year in years" :key="year">
                    <tr>
                        <td>{{ year }}</td>
                        <template v-for="(value, monthIndex) in getYearData(year)" :key="year + '-month-' + monthIndex">
                            <td>{{ valueDisplay(value) }}</td>
                        </template>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import { ref, computed, watch, onCreated } from 'vue';

// Props
const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

// 狀態
const yearData = ref({});

// 計算屬性：月份
const months = computed(() => [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]);

// 計算屬性：年份範圍
const years = computed(() => {
  const startYear = new Date(props.data.時間起點).getFullYear();
  const endYear = new Date(props.data.時間終點).getFullYear();
  const result = [];
  for (let year = startYear; year <= endYear; year++) {
    result.push(year);
  }
  return result;
});

// 方法：取得某年份的資料
function getYearData(year) {
  return yearData.value[year];
}

// 方法：初始化資料處理
function processInitData() {
  const startMonth = new Date(props.data.時間起點).getMonth() + 1;
  const endMonth = new Date(props.data.時間終點).getMonth() + 1;
  const startYear = new Date(props.data.時間起點).getFullYear();
  const endYear = new Date(props.data.時間終點).getFullYear();

  const rawPrices = props.data.統計值.split(',');
  const result = {};

  for (let year = startYear; year <= endYear; year++) {
    const yearPrices = [];
    for (let month = 1; month <= 12; month++) {
      if (year === startYear && month < startMonth) {
        yearPrices.push('0');
      } else if (year === endYear && month > endMonth) {
        yearPrices.push('0');
      } else {
        const index = month + (year - startYear) * 12 - startMonth;
        yearPrices.push(rawPrices[index] || '0');
      }
    }
    result[year] = yearPrices;
  }

  yearData.value = result;
}

// 方法：顯示數值
function valueDisplay(value) {
  return value === '0' ? '-' : value;
}

// 初始化
onCreated(() => {
  processInitData();
});

// 監聽 props.data 變化
watch(() => props.data, (newVal) => {
  if (newVal) {
    processInitData();
  }
}, { deep: true });
</script>

<style scoped>
.trending-table {
    margin-top: 2em;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    border: 1px solid #ccc;
    padding: 0.5em;
    text-align: center;
}
</style>