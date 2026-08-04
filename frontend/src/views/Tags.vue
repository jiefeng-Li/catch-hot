<template>
  <div class="page-container">
    <el-card class="page-card" shadow="never">
      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="openDialog()"
          >新增标签</el-button
        >
        <el-button :icon="Refresh" @click="loadTags">刷新</el-button>
      </div>

      <el-table :data="tags" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column label="关键词" min-width="180">
          <template #default="{ row }">
            <template v-if="row.keywords && row.keywords.length">
              <el-tag
                v-for="kw in row.keywords"
                :key="kw"
                size="small"
                style="margin-right: 4px; margin-bottom: 4px"
              >
                {{ kw }}
              </el-tag>
            </template>
            <span v-else-if="row.keyword">{{ row.keyword }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="平台范围" min-width="180">
          <template #default="{ row }">
            <template v-if="row.platforms && row.platforms.length">
              <el-tag
                v-for="p in row.platforms"
                :key="p"
                size="small"
                style="margin-right: 4px"
              >
                {{ platformLabel(p) }}
              </el-tag>
            </template>
            <el-tag v-else size="small" type="info">全部平台</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="抓取频率" width="110" align="center">
          <template #default="{ row }"
            >每 {{ row.interval_minutes }} 分钟</template
          >
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? "运行中" : "已暂停" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" align="center">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openDialog(row)"
              >编辑</el-button
            >
            <el-button
              size="small"
              text
              :type="row.enabled ? 'warning' : 'success'"
              @click="toggle(row)"
            >
              {{ row.enabled ? "暂停" : "启用" }}
            </el-button>
            <el-button
              size="small"
              text
              type="primary"
              :loading="row._fetching"
              @click="trigger(row)"
            >
              立即抓取
            </el-button>
            <el-popconfirm
              title="确认删除该标签？历史数据将保留"
              @confirm="remove(row)"
            >
              <template #reference>
                <el-button size="small" text type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无标签，点击「新增标签」开始监控" />
        </template>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑标签' : '新增标签'"
      width="480px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="如：AI 编程工具"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="关键词" prop="keywordsText">
          <el-input
            v-model="form.keywordsText"
            type="textarea"
            :rows="3"
            placeholder="输入多个关键词，英文逗号或换行分隔"
          />
          <div style="margin-top: 6px; color: #909399; font-size: 12px">
            支持同时监控多个关键词；旧的单关键词也会兼容显示。
          </div>
        </el-form-item>
        <el-form-item label="平台范围">
          <el-select
            v-model="form.platforms"
            multiple
            clearable
            placeholder="不选则为全部平台"
            style="width: 100%"
          >
            <el-option
              v-for="p in platformOptions"
              :key="p.value"
              :label="p.label"
              :value="p.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="抓取频率">
          <el-input-number
            v-model="form.interval_minutes"
            :min="1"
            :max="1440"
          />
          <span style="margin-left: 8px; color: #909399">分钟/次</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { Plus, Refresh } from "@element-plus/icons-vue";
import { metaApi, tagApi } from "../api";

const tags = ref([]);
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref();
const platformOptions = ref([]);

const emptyForm = {
  id: null,
  name: "",
  keyword: "",
  keywordsText: "",
  platforms: [],
  interval_minutes: 60,
};
const form = reactive({ ...emptyForm });

const rules = {
  name: [{ required: true, message: "请输入名称", trigger: "blur" }],
  keywordsText: [
    { required: true, message: "请输入至少一个关键词", trigger: "blur" },
  ],
};

const platformLabel = (value) =>
  platformOptions.value.find((p) => p.value === value)?.label ?? value;

async function loadTags() {
  loading.value = true;
  try {
    tags.value = await tagApi.list();
  } finally {
    loading.value = false;
  }
}

function openDialog(row) {
  Object.assign(
    form,
    emptyForm,
    row
      ? {
          id: row.id,
          name: row.name,
          keyword: row.keyword ?? "",
          keywordsText:
            row.keywords && row.keywords.length
              ? row.keywords.join(", ")
              : (row.keyword ?? ""),
          platforms: row.platforms ?? [],
          interval_minutes: row.interval_minutes,
        }
      : {},
  );
  dialogVisible.value = true;
}

async function save() {
  await formRef.value.validate();
  saving.value = true;
  try {
    const keywords = form.keywordsText
      .split(/[\n,，]+/)
      .map((item) => item.trim())
      .filter(Boolean);
    const payload = {
      name: form.name,
      keyword: keywords[0] ?? form.keyword,
      keywords,
      platforms: form.platforms.length ? form.platforms : null,
      interval_minutes: form.interval_minutes,
    };
    if (form.id) {
      await tagApi.update(form.id, payload);
      ElMessage.success("标签已更新");
    } else {
      await tagApi.create(payload);
      ElMessage.success("标签已创建");
    }
    dialogVisible.value = false;
    await loadTags();
  } finally {
    saving.value = false;
  }
}

async function toggle(row) {
  const updated = await tagApi.toggle(row.id);
  ElMessage.success(
    updated.enabled ? "已启用，将继续定时抓取" : "已暂停，不再触发抓取",
  );
  await loadTags();
}

async function trigger(row) {
  row._fetching = true;
  try {
    const jobs = await tagApi.triggerFetch(row.id);
    const saved = jobs.reduce((sum, j) => sum + j.items_saved, 0);
    const failed = jobs.filter((j) => j.status === "failed");
    if (failed.length) {
      ElMessage.warning(
        `抓取完成，新增 ${saved} 条；${failed.length} 个平台失败，详见任务日志`,
      );
    } else {
      ElMessage.success(`抓取完成，新增 ${saved} 条热点`);
    }
  } finally {
    row._fetching = false;
  }
}

async function remove(row) {
  await tagApi.remove(row.id);
  ElMessage.success("已删除（历史数据保留）");
  await loadTags();
}

onMounted(async () => {
  await loadTags();
  try {
    const health = await metaApi.health();
    platformOptions.value = health.platforms.map((p) => ({
      value: p,
      label: p,
    }));
  } catch {
    platformOptions.value = [];
  }
});
</script>
