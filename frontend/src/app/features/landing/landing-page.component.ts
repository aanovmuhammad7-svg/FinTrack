import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="landing">
      <header class="hero">
        <div class="hero-copy">
          <p class="eyebrow">FinTrack</p>
          <h1>Финансы под контролем, а не в заметках и хаосе.</h1>
          <p class="lead">
            FinTrack помогает вести категории, операции, бюджеты и отчёты в одном месте.
            Это веб-приложение для тех, кому важно видеть не только отдельные траты,
            но и целую картину своих денег.
          </p>

          <div class="hero-actions">
            <a class="cta" routerLink="/register">Начать с регистрации</a>
            <a class="secondary" routerLink="/login">У меня уже есть аккаунт</a>
          </div>
        </div>

        <div class="hero-card">
          <p class="card-label">Что внутри</p>
          <div class="metric">
            <span>Категории</span>
            <strong>доходы и расходы</strong>
          </div>
          <div class="metric">
            <span>Операции</span>
            <strong>история движения денег</strong>
          </div>
          <div class="metric">
            <span>Бюджеты</span>
            <strong>контроль лимитов</strong>
          </div>
          <div class="metric">
            <span>Отчёты</span>
            <strong>обзор периода и структуры трат</strong>
          </div>
        </div>
      </header>

      <section class="info-grid">
        <article class="info-card">
          <p class="section-tag">Для чего</p>
          <h2>Чтобы видеть, куда реально уходят деньги</h2>
          <p>
            Вместо разрозненных таблиц и заметок вы получаете единое пространство:
            категории, транзакции, бюджеты и аналитика связаны между собой.
          </p>
        </article>

        <article class="info-card dark">
          <p class="section-tag">Почему удобно</p>
          <ul>
            <li>Добавление операций без лишней рутины</li>
            <li>Бюджеты показывают прогресс автоматически</li>
            <li>Отчёты собираются на тех же данных, что и повседневная работа</li>
          </ul>
        </article>
      </section>

      <section class="feature-strip">
        <article>
          <span>01</span>
          <h3>Наведите порядок</h3>
          <p>Сначала создайте категории и получите понятную структуру ваших финансов.</p>
        </article>
        <article>
          <span>02</span>
          <h3>Следите за движением</h3>
          <p>Фиксируйте доходы и расходы, не теряя контекст и историю.</p>
        </article>
        <article>
          <span>03</span>
          <h3>Держите рамки</h3>
          <p>Бюджеты и сводка помогают не замечать проблему слишком поздно.</p>
        </article>
      </section>

      <section class="invite">
        <div class="invite-copy">
          <p class="section-tag">Следующий шаг</p>
          <h2>Если хотите начать аккуратно вести финансы, зарегистрируйтесь.</h2>
          <p>
            После регистрации вы сможете сразу войти в приложение, создать первые категории и
            получить рабочую финансовую панель.
          </p>
        </div>

        <a class="cta large" routerLink="/register">Перейти к регистрации</a>
      </section>
    </section>
  `,
  styles: [`
    :host {
      display: block;
    }

    .landing {
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
      padding: 26px 0 44px;
      display: grid;
      gap: 24px;
    }

    .hero,
    .info-grid,
    .feature-strip,
    .invite {
      display: grid;
      gap: 22px;
    }

    .hero {
      grid-template-columns: 1.2fr 0.8fr;
      align-items: stretch;
    }

    .hero-copy,
    .hero-card,
    .info-card,
    .invite {
      border-radius: 32px;
      border: 1px solid rgba(104, 72, 52, 0.12);
      box-shadow: 0 24px 60px rgba(40, 29, 21, 0.12);
      overflow: hidden;
    }

    .hero-copy {
      padding: 34px;
      background:
        radial-gradient(circle at top left, rgba(228, 167, 88, 0.24), transparent 20rem),
        linear-gradient(135deg, rgba(61, 48, 38, 0.96), rgba(29, 24, 20, 0.96));
      color: #f9eedc;
      display: grid;
      gap: 16px;
      align-content: center;
    }

    .eyebrow,
    .section-tag,
    .card-label {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 0.76rem;
      font-weight: 700;
    }

    .eyebrow {
      color: rgba(255, 224, 182, 0.9);
    }

    h1,
    h2,
    h3 {
      margin: 0;
      line-height: 0.96;
      letter-spacing: -0.04em;
    }

    h1 {
      font-size: clamp(3rem, 7vw, 6rem);
      max-width: 11ch;
    }

    h2 {
      font-size: clamp(2rem, 4vw, 3.2rem);
      color: #30231b;
    }

    h3 {
      font-size: 1.4rem;
      color: #32251d;
    }

    .lead,
    .invite p,
    .info-card p,
    .feature-strip p {
      margin: 0;
      line-height: 1.7;
    }

    .lead {
      max-width: 55ch;
      color: rgba(249, 238, 220, 0.8);
      font-size: 1.04rem;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin-top: 10px;
    }

    .cta,
    .secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      font-weight: 700;
      border-radius: 999px;
      padding: 14px 22px;
      transition: transform 180ms ease, box-shadow 180ms ease;
    }

    .cta {
      background: linear-gradient(135deg, #c96d37, #8f4527);
      color: #fff8f1;
      box-shadow: 0 14px 24px rgba(143, 69, 39, 0.24);
    }

    .secondary {
      background: rgba(255, 246, 231, 0.12);
      border: 1px solid rgba(255, 228, 192, 0.16);
      color: #f9eedc;
    }

    .cta:hover,
    .secondary:hover {
      transform: translateY(-1px);
    }

    .hero-card {
      padding: 30px;
      background:
        radial-gradient(circle at top right, rgba(116, 143, 230, 0.16), transparent 18rem),
        linear-gradient(135deg, rgba(255, 251, 245, 0.94), rgba(244, 234, 220, 0.9));
      display: grid;
      gap: 14px;
      align-content: center;
    }

    .card-label,
    .section-tag {
      color: #a85c31;
    }

    .metric {
      padding: 18px;
      border-radius: 22px;
      background: rgba(255, 251, 246, 0.82);
      border: 1px solid rgba(104, 72, 52, 0.08);
      display: grid;
      gap: 8px;
    }

    .metric span {
      color: #7a675b;
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .metric strong {
      color: #30231b;
      font-size: 1.08rem;
    }

    .info-grid {
      grid-template-columns: 1fr 1fr;
    }

    .info-card {
      padding: 28px;
      background: rgba(255, 250, 244, 0.9);
      display: grid;
      gap: 14px;
    }

    .info-card p,
    .info-card li,
    .invite p {
      color: #6b5b50;
    }

    .dark {
      background:
        radial-gradient(circle at top left, rgba(104, 134, 213, 0.2), transparent 18rem),
        linear-gradient(135deg, rgba(34, 37, 54, 0.96), rgba(28, 24, 37, 0.96));
    }

    .dark .section-tag,
    .dark h2,
    .dark li {
      color: #f4f0ff;
    }

    .dark .section-tag {
      color: rgba(197, 208, 255, 0.88);
    }

    .dark ul {
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 10px;
      line-height: 1.6;
    }

    .feature-strip {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .feature-strip article {
      padding: 24px;
      border-radius: 28px;
      background: rgba(255, 249, 240, 0.84);
      border: 1px solid rgba(104, 72, 52, 0.1);
      box-shadow: 0 18px 44px rgba(40, 29, 21, 0.1);
      display: grid;
      gap: 10px;
    }

    .feature-strip span {
      color: #b16a37;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-weight: 700;
    }

    .invite {
      grid-template-columns: 1fr auto;
      align-items: center;
      padding: 30px;
      background:
        radial-gradient(circle at top right, rgba(228, 167, 88, 0.22), transparent 18rem),
        linear-gradient(135deg, rgba(255, 251, 245, 0.94), rgba(244, 234, 220, 0.9));
    }

    .invite-copy {
      display: grid;
      gap: 12px;
    }

    .large {
      padding-inline: 28px;
    }

    @media (max-width: 1100px) {
      .hero,
      .info-grid,
      .feature-strip,
      .invite {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 720px) {
      .landing {
        width: min(100% - 20px, 100%);
        padding-top: 18px;
      }

      .hero-copy,
      .hero-card,
      .info-card,
      .invite,
      .feature-strip article {
        padding: 22px;
      }
    }
  `],
})
export class LandingPageComponent {}
