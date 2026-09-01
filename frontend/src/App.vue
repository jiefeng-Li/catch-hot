<template>
  <template v-if="route.meta.layout !== 'home'">
    <el-container class="app-layout">
      <el-aside width="240px" class="app-aside">
        <div class="logo">
          <div class="logo-icon">
            <el-icon :size="20"><Sunny /></el-icon>
          </div>
          <div>
            <div class="logo-title">CatchHot</div>
            <div class="logo-subtitle">热点追踪面板</div>
          </div>
        </div>

        <el-menu
          :default-active="$route.path"
          router
          class="side-menu"
          active-text-color="#2563eb"
          background-color="transparent"
          text-color="#475569"
        >
          <el-menu-item index="/app/hot">
            <el-icon><HotWater /></el-icon>
            <span>热点列表</span>
          </el-menu-item>
          <el-menu-item index="/app/tags">
            <el-icon><CollectionTag /></el-icon>
            <span>标签管理</span>
          </el-menu-item>
          <el-menu-item index="/app/trend">
            <el-icon><TrendCharts /></el-icon>
            <span>趋势分析</span>
          </el-menu-item>
          <el-menu-item index="/app/jobs">
            <el-icon><Document /></el-icon>
            <span>任务日志</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container class="app-content">
        <el-header class="app-header" height="72px">
          <div class="header-left">
            <div class="header-dot"></div>
            <div>
              <div class="page-title">{{ $route.meta.title }}</div>
              <div class="page-subtitle">{{ headerSubtitle }}</div>
            </div>
          </div>
          <div class="header-badge">实时更新</div>
        </el-header>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </template>

  <router-view v-else />
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const headerSubtitle = computed(() => {
  const title = route.meta.title;
  if (title === "热点列表") return "持续抓取并聚合跨平台热点内容";
  if (title === "标签管理") return "配置监控策略与抓取频率";
  if (title === "趋势分析") return "分析内容热度变化与平台分布";
  return "查看抓取任务执行状态";
});
</script>

<style scoped>
.app-layout {
  height: 100%;
  background: linear-gradient(135deg, #f7faff 0%, #f3f7ff 100%);
}

.app-aside {
  background: linear-gradient(180deg, #f8fbff 0%, #f2f6ff 100%);
  border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 72px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  color: #2563eb;
  background: linear-gradient(135deg, #dbeafe, #e0f2fe);
}

.logo-title {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

.logo-subtitle {
  font-size: 12px;
  color: #64748b;
}

.side-menu {
  border-right: none;
  padding: 16px 12px;
}

:deep(.el-menu-item) {
  margin-bottom: 6px;
  border-radius: 12px;
  transition: all 0.2s ease;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(
    90deg,
    rgba(37, 99, 235, 0.12),
    rgba(37, 99, 235, 0.05)
  );
  font-weight: 600;
}

:deep(.el-menu-item:hover) {
  background: rgba(37, 99, 235, 0.08);
}

.app-content {
  background: transparent;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  backdrop-filter: blur(8px);
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #38bdf8);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.page-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.page-subtitle {
  font-size: 12px;
  color: #64748b;
}

.header-badge {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: #2563eb;
  background: rgba(37, 99, 235, 0.08);
}

.app-main {
  padding: 0;
  overflow-y: auto;
}
</style>
