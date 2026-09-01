<template>
  <div class="home-shell">
    <header class="hero">
      <nav class="topbar">
        <div class="brand">
          <span class="brand-mark">J</span>
          <span>Jie Feng Li</span>
        </div>
        <div class="nav-links">
          <a href="#projects">作品</a>
          <a href="#about">关于</a>
          <a href="#contact">联系</a>
          <router-link to="/app/hot" class="nav-button"
            >查看 CatchHot</router-link
          >
        </div>
      </nav>

      <div class="hero-content">
        <div class="hero-copy">
          <span class="eyebrow">个人主页 / Portfolio</span>
          <h1>我在构建更有价值的产品与实践。</h1>
          <p>
            我热爱开发、数据可视化和自动化工具，关注热点内容、产品体验与工程效率。
            这里汇总了我的作品、项目与实践经验，也欢迎你访问 CatchHot
            这个实时热点追踪应用。
          </p>
          <div class="cta-row">
            <router-link to="/app/hot" class="primary-btn"
              >打开 CatchHot</router-link
            >
            <a href="#projects" class="secondary-btn">查看项目</a>
          </div>
        </div>

        <div class="hero-panel">
          <div class="panel-card featured-project">
            <div class="project-label">Featured Project</div>
            <h3>CatchHot</h3>
            <p>
              一个聚合热点内容、标签趋势与抓取任务的监控平台，帮助快速掌握跨平台热度变化。
            </p>
            <ul>
              <li>实时热点聚合</li>
              <li>标签与趋势分析</li>
              <li>任务日志追踪</li>
            </ul>
            <router-link to="/app/hot">进入项目 →</router-link>
          </div>
        </div>
      </div>
    </header>

    <main class="home-main">
      <a
        class="icp-badge"
        href="https://beian.miit.gov.cn/"
        target="_blank"
        rel="noopener noreferrer"
      >
        蜀ICP备2026045444号
      </a>

      <section id="projects" class="section-block">
        <div class="section-head">
          <span class="section-kicker">Projects</span>
          <h2>作品与项目</h2>
        </div>

        <div class="project-grid">
          <article class="project-card main-project">
            <div class="card-top">
              <span class="tag">Web App</span>
              <span class="dot-live">Live</span>
            </div>
            <h3>CatchHot</h3>
            <p>
              聚合来自不同平台的热点信息，支持标签管理、趋势分析与抓取任务监控，适合日常热点追踪与分析。
            </p>
            <div class="tech-stack">
              <span>Vue</span>
              <span>FastAPI</span>
              <span>MySQL</span>
            </div>
            <router-link to="/app/hot">访问项目</router-link>
          </article>

          <article class="project-card">
            <div class="card-top">
              <span class="tag">Tooling</span>
            </div>
            <h3>内容监控脚本</h3>
            <p>
              用于批量抓取、清洗与汇总多平台内容数据，为热点分析提供稳定的数据来源。
            </p>
            <div class="tech-stack">
              <span>Python</span>
              <span>Scheduler</span>
            </div>
          </article>

          <article class="project-card">
            <div class="card-top">
              <span class="tag">Data</span>
            </div>
            <h3>趋势观察台</h3>
            <p>
              对多个关键词和主题的增长曲线进行视觉化展示，便于识别突发事件和内容变化规律。
            </p>
            <div class="tech-stack">
              <span>ECharts</span>
              <span>Analytics</span>
            </div>
          </article>
        </div>
      </section>

      <section id="about" class="section-block about-block">
        <div class="section-head">
          <span class="section-kicker">About</span>
          <h2>关于我</h2>
        </div>
        <div class="about-grid">
          <div>
            <p>
              我关注真实问题与产品落地，擅长从需求出发做原型、实现和迭代，综合运用前端、后端、数据库与自动化能力。
            </p>
          </div>
          <div class="meta-list">
            <div>
              <strong>方向</strong><span>Web 产品 · 数据应用 · 工程化</span>
            </div>
            <div>
              <strong>技能</strong
              ><span>Vue / FastAPI / Python / MySQL / 数据分析</span>
            </div>
            <div>
              <strong>状态</strong><span>持续学习中，欢迎项目合作</span>
            </div>
          </div>
        </div>
      </section>

      <section id="contact" class="section-block contact-block">
        <div class="section-head">
          <span class="section-kicker">Contact</span>
          <h2>联系我</h2>
        </div>
        <div class="contact-box">
          <p>
            如果你对我的作品或项目感兴趣，欢迎联系我讨论合作、交流和新想法。
          </p>
          <a href="mailto:hello@jiefengli.site">hello@jiefengli.site</a>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup></script>

<style scoped>
.home-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at top, rgba(59, 130, 246, 0.18), transparent 30%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
  color: #0f172a;
}

.hero {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px 48px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 0 24px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 1.1rem;
  font-weight: 700;
}

.brand-mark {
  display: inline-flex;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2563eb, #38bdf8);
  color: #fff;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.22);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-links a {
  color: #334155;
  text-decoration: none;
  font-weight: 600;
}

.nav-button,
.primary-btn,
.secondary-btn,
.contact-box a,
.project-card a,
.featured-project a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  text-decoration: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.nav-button,
.primary-btn {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #fff;
  padding: 10px 18px;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.18);
}

.secondary-btn {
  padding: 10px 18px;
  border: 1px solid rgba(37, 99, 235, 0.15);
  background: rgba(255, 255, 255, 0.8);
  color: #1d4ed8;
}

.hero-content {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  align-items: center;
  gap: 28px;
  padding-top: 20px;
}

.eyebrow,
.section-kicker,
.project-label {
  display: inline-block;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #2563eb;
  font-weight: 700;
}

.hero-copy h1 {
  margin: 16px 0 18px;
  font-size: clamp(2.4rem, 5vw, 4.2rem);
  line-height: 1.08;
  letter-spacing: -0.04em;
}

.hero-copy p {
  max-width: 620px;
  font-size: 1.08rem;
  line-height: 1.8;
  color: #475569;
}

.cta-row {
  display: flex;
  gap: 16px;
  margin-top: 28px;
  flex-wrap: wrap;
}

.hero-panel {
  display: flex;
  justify-content: center;
}

.panel-card {
  width: min(100%, 420px);
  padding: 26px 22px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(8px);
}

.featured-project h3,
.project-card h3 {
  margin: 8px 0 10px;
  font-size: 1.7rem;
}

.featured-project p,
.project-card p,
.contact-box p,
.about-grid p {
  color: #475569;
  line-height: 1.8;
}

.featured-project ul {
  margin: 18px 0;
  padding-left: 18px;
  color: #334155;
  line-height: 1.9;
}

.featured-project a,
.project-card a {
  color: #2563eb;
  font-weight: 700;
}

.home-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px 72px;
  position: relative;
}

.icp-badge {
  position: fixed;
  right: 20px;
  bottom: 18px;
  z-index: 50;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  font-size: 0.8rem;
  text-decoration: none;
  letter-spacing: 0.02em;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(8px);
}

.icp-badge:hover {
  background: rgba(15, 23, 42, 0.82);
}

.section-block {
  margin-top: 36px;
  padding: 28px 0;
}

.section-head {
  margin-bottom: 22px;
}

.section-head h2 {
  margin: 10px 0 0;
  font-size: clamp(1.8rem, 3vw, 2.5rem);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
}

.project-card {
  padding: 24px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 24px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.04);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.tag {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 700;
}

.dot-live {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #16a34a;
  font-size: 0.75rem;
  font-weight: 700;
}

.dot-live::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  display: inline-block;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 18px 0 18px;
}

.tech-stack span {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 0.72rem;
  font-weight: 700;
}

.about-grid {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 22px;
  padding: 18px 0 0;
}

.meta-list {
  display: grid;
  gap: 14px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 20px;
  padding: 20px;
}

.meta-list div {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.meta-list div:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.meta-list strong {
  color: #0f172a;
}

.meta-list span {
  color: #475569;
  text-align: right;
}

.contact-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 24px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 20px;
}

.contact-box a {
  padding: 10px 18px;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 700;
}

.nav-button:hover,
.primary-btn:hover,
.secondary-btn:hover,
.contact-box a:hover,
.project-card a:hover,
.featured-project a:hover {
  transform: translateY(-1px);
}

@media (max-width: 900px) {
  .hero-content,
  .about-grid,
  .project-grid {
    grid-template-columns: 1fr;
  }

  .contact-box,
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-links {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
