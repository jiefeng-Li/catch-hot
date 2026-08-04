<template>
  <div class="page-container">
    <el-card class="page-card" shadow="never">
      <!-- 筛选工具栏（需求 7.4：平台/时间/关键词二次筛选，时间/热度排序） -->
      <div class="toolbar">
        <el-select
          v-model="query.tag_id"
          placeholder="全部标签"
          clearable
          style="width: 160px"
          @change="reload"
        >
          <el-option
            v-for="t in tags"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          />
        </el-select>
        <el-select
          v-model="query.platform"
          placeholder="全部平台"
          clearable
          style="width: 140px"
          @change="reload"
        >
          <el-option label="知乎" value="zhihu" />
          <el-option label="B站" value="bilibili" />
          <el-option label="GitHub" value="github" />
        </el-select>
        <el-select
          v-model="query.hours"
          placeholder="全部时间"
          clearable
          style="width: 130px"
          @change="reload"
        >
          <el-option label="最近 1 小时" :value="1" />
          <el-option label="最近 6 小时" :value="6" />
          <el-option label="最近 24 小时" :value="24" />
          <el-option label="最近 7 天" :value="168" />
        </el-select>
        <el-input
          v-model="query.keyword"
          placeholder="标题/摘要关键词"
          clearable
          style="width: 200px"
          @keyup.enter="reload"
          @clear="reload"
        />
        <el-radio-group v-model="query.sort" @change="reload">
          <el-radio-button value="time">按时间</el-radio-button>
          <el-radio-button value="hot">按热度</el-radio-button>
        </el-radio-group>
        <el-button type="primary" :icon="Search" @click="reload"
          >查询</el-button
        >
        <el-button type="warning" plain @click="resetAndRefetch"
          >清空并重抓</el-button
        >
      </div>

      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column label="标题" min-width="320">
          <template #default="{ row }">
            <a
              class="link-title"
              :href="row.url"
              target="_blank"
              rel="noopener"
              >{{ row.title }}</a
            >
            <div v-if="row.summary" class="summary">{{ row.summary }}</div>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="platformTagType(row.platform)">{{
              platformLabel(row.platform)
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="综合评分"
          width="120"
          align="center"
          sortable
          :sort-method="(a, b) => a.score - b.score"
        >
          <template #default="{ row }">
            <div
              class="score-pill"
              :style="{ backgroundColor: scoreBadgeColor(row.score) }"
            >
              {{ (row.score ?? 0).toFixed(0) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="抓取时间" width="170" align="center">
          <template #default="{ row }">{{
            formatTime(row.fetched_at)
          }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="open(row)"
              >原文</el-button
            >
          </template>
        </el-table-column>
        <template #empty>
          <el-empty
            description="暂无热点数据，请先在「标签管理」创建标签并抓取"
          />
        </template>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="query.limit"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="load"
        @size-change="reload"
      />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { itemApi, tagApi } from "../api";

const tags = ref([]);
const items = ref([]);
const total = ref(0);
const page = ref(1);
const loading = ref(false);

const query = reactive({
  tag_id: null,
  platform: null,
  keyword: null,
  hours: null,
  sort: "time",
  limit: 50,
});

const PLATFORM_MAP = {
  zhihu: { label: "知乎", type: "primary" },
  bilibili: { label: "B站", type: "danger" },
  github: { label: "GitHub", type: "info" },
};
const platformLabel = (p) => PLATFORM_MAP[p]?.label ?? p;
const platformTagType = (p) => PLATFORM_MAP[p]?.type ?? "info";

function scoreBadgeColor(score) {
  if (score >= 80) return "#fee2e2";
  if (score >= 50) return "#fef3c7";
  return "#f3f4f6";
}

function formatTime(iso) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString("zh-CN", { hour12: false });
}

function open(row) {
  window.open(row.url, "_blank", "noopener");
}

async function load() {
  loading.value = true;
  try {
    const params = {
      ...query,
      offset: (page.value - 1) * query.limit,
    };
    Object.keys(params).forEach(
      (k) => (params[k] == null || params[k] === "") && delete params[k],
    );
    const data = await itemApi.list(params);
    items.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function reload() {
  page.value = 1;
  load();
}

async function resetAndRefetch() {
  try {
    await ElMessageBox.confirm(
      "这会清空当前所有热点历史和任务记录，并重新抓取标签数据。是否继续？",
      "确认重置",
      { confirmButtonText: "继续", cancelButtonText: "取消", type: "warning" },
    );

    loading.value = true;
    await itemApi.resetData();
    const freshTags = await tagApi.list();
    tags.value = freshTags;
    for (const tag of freshTags) {
      await tagApi.triggerFetch(tag.id);
    }
    ElMessage.success("已清空并开始重新抓取");
    await load();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("重置失败，请稍后再试");
    }
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  tags.value = await tagApi.list();
  await load();
});
</script>

<style scoped>
.summary {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

:deep(.el-table__row) {
  transition: background-color 0.2s ease;
}

:deep(.el-tag) {
  border-radius: 999px;
}
</style>
