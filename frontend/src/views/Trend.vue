<template>
  <div class="page-container">
    <el-card class="page-card" shadow="never">
      <div class="toolbar">
        <el-select
          v-model="tagId"
          placeholder="选择标签"
          style="width: 200px"
          @change="loadAll"
        >
          <el-option
            v-for="t in tags"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          />
        </el-select>
        <el-radio-group v-model="days" @change="loadTrend">
          <el-radio-button :value="7">近 7 天</el-radio-button>
          <el-radio-button :value="30">近 30 天</el-radio-button>
        </el-radio-group>
      </div>

      <el-empty v-if="!tagId" description="请选择一个标签查看趋势" />
      <template v-else>
        <div ref="trendChartRef" class="chart" v-loading="loading"></div>
        <el-divider />
        <h3 class="dist-title">来源平台分布</h3>
        <div ref="distChartRef" class="chart chart-small"></div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import { tagApi, trendApi } from "../api";

const tags = ref([]);
const tagId = ref(null);
const days = ref(7);
const loading = ref(false);

const trendChartRef = ref();
const distChartRef = ref();
let trendChart = null;
let distChart = null;

async function loadTrend() {
  if (!tagId.value) return;
  loading.value = true;
  try {
    const data = await trendApi.trend(tagId.value, days.value);
    await nextTick();
    renderTrend(data);
  } finally {
    loading.value = false;
  }
}

async function loadDistribution() {
  if (!tagId.value) return;
  const data = await trendApi.distribution(tagId.value);
  await nextTick();
  renderDist(data);
}

function loadAll() {
  loadTrend();
  loadDistribution();
}

function renderTrend(data) {
  if (!trendChart) trendChart = echarts.init(trendChartRef.value);
  trendChart.setOption({
    tooltip: { trigger: "axis" },
    legend: { data: ["抓取数量", "热度总量"] },
    grid: { left: 50, right: 50, top: 40, bottom: 30 },
    xAxis: { type: "category", data: data.map((d) => d.date) },
    yAxis: [
      { type: "value", name: "数量" },
      { type: "value", name: "热度" },
    ],
    series: [
      {
        name: "抓取数量",
        type: "line",
        smooth: true,
        areaStyle: { opacity: 0.15 },
        data: data.map((d) => d.count),
      },
      {
        name: "热度总量",
        type: "bar",
        yAxisIndex: 1,
        itemStyle: { color: "#e6a23c", opacity: 0.7 },
        data: data.map((d) => d.total_hot),
      },
    ],
  });
}

function renderDist(data) {
  if (!distChart) distChart = echarts.init(distChartRef.value);
  distChart.setOption({
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0 },
    series: [
      {
        type: "pie",
        radius: ["40%", "65%"],
        center: ["50%", "45%"],
        label: { formatter: "{b}\n{c} 条" },
        data: data.map((d) => ({ name: d.platform, value: d.count })),
      },
    ],
  });
}

function handleResize() {
  trendChart?.resize();
  distChart?.resize();
}

onMounted(async () => {
  tags.value = await tagApi.list();
  if (tags.value.length) {
    tagId.value = tags.value[0].id;
    loadAll();
  }
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  trendChart?.dispose();
  distChart?.dispose();
});
</script>

<style scoped>
.chart {
  height: 360px;
  width: 100%;
  padding: 8px;
  border: 1px solid var(--app-border);
  border-radius: 16px;
  background: linear-gradient(135deg, #fcfdff 0%, #f8fbff 100%);
}

.chart-small {
  height: 300px;
}

.dist-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}
</style>
