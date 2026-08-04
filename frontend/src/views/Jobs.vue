<template>
  <div class="page-container">
    <el-card class="page-card" shadow="never">
      <div class="toolbar">
        <el-select
          v-model="query.tag_id"
          placeholder="全部标签"
          clearable
          style="width: 180px"
          @change="load"
        >
          <el-option
            v-for="t in tags"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          />
        </el-select>
        <el-select
          v-model="query.status"
          placeholder="全部状态"
          clearable
          style="width: 130px"
          @change="load"
        >
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="运行中" value="running" />
        </el-select>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>

      <el-table :data="jobs" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column label="标签" width="140">
          <template #default="{ row }">{{ tagName(row.tag_id) }}</template>
        </el-table-column>
        <el-table-column label="平台" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)">{{
              statusLabel(row.status)
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="retry_count"
          label="重试"
          width="70"
          align="center"
        />
        <el-table-column label="抓取/入库" width="100" align="center">
          <template #default="{ row }"
            >{{ row.items_fetched }} / {{ row.items_saved }}</template
          >
        </el-table-column>
        <el-table-column label="开始时间" width="165" align="center">
          <template #default="{ row }">{{
            formatTime(row.started_at)
          }}</template>
        </el-table-column>
        <el-table-column label="耗时" width="90" align="center">
          <template #default="{ row }">{{ duration(row) }}</template>
        </el-table-column>
        <el-table-column label="错误信息" min-width="200">
          <template #default="{ row }">
            <span v-if="row.error_message" class="error-text">{{
              row.error_message
            }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无任务记录" />
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { Refresh } from "@element-plus/icons-vue";
import { jobApi, tagApi } from "../api";

const tags = ref([]);
const jobs = ref([]);
const loading = ref(false);

const query = reactive({ tag_id: null, status: null });

const tagName = (id) => tags.value.find((t) => t.id === id)?.name ?? `#${id}`;

const STATUS_MAP = {
  success: { label: "成功", type: "success" },
  failed: { label: "失败", type: "danger" },
  running: { label: "运行中", type: "warning" },
};
const statusLabel = (s) => STATUS_MAP[s]?.label ?? s;
const statusType = (s) => STATUS_MAP[s]?.type ?? "info";

function formatTime(iso) {
  if (!iso) return "-";
  return new Date(iso).toLocaleString("zh-CN", { hour12: false });
}

function duration(row) {
  if (!row.finished_at) return "-";
  const ms = new Date(row.finished_at) - new Date(row.started_at);
  return `${(ms / 1000).toFixed(1)}s`;
}

async function load() {
  loading.value = true;
  try {
    const params = { limit: 100 };
    if (query.tag_id) params.tag_id = query.tag_id;
    if (query.status) params.status = query.status;
    jobs.value = await jobApi.list(params);
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
.error-text {
  color: #f56c6c;
  font-size: 12px;
}

:deep(.el-table__row) {
  transition: background-color 0.2s ease;
}
</style>
