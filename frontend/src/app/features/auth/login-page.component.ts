import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <section class="auth-layout">
      <aside class="story-panel">
        <p class="eyebrow">FinTrack</p>
        <h1>Деньги любят ясную картину.</h1>
        <p class="lead">
          Вход ведёт не просто в приложение, а в аккуратно собранную финансовую систему:
          категории, движение денег, бюджеты и отчёты уже ждут внутри.
        </p>

        <div class="story-grid">
          <article>
            <span>01</span>
            <strong>Быстрая фиксация операций</strong>
            <p>Добавляйте доходы и расходы без лишней рутины.</p>
          </article>
          <article>
            <span>02</span>
            <strong>Контроль лимитов</strong>
            <p>Бюджеты показывают, где вы уже выходите за рамки.</p>
          </article>
          <article>
            <span>03</span>
            <strong>Живой обзор периода</strong>
            <p>Сводка и отчёты собираются на тех же данных, что и операции.</p>
          </article>
        </div>
      </aside>

      <section class="form-panel">
        <div class="form-shell">
          <a class="back-link" routerLink="/">← На главную</a>
          <p class="form-kicker">Авторизация</p>
          <h2>Войти в рабочее пространство</h2>
          <p class="form-copy">Используйте email и пароль, чтобы продолжить с уже сохранёнными данными.</p>

          <form [formGroup]="form" (ngSubmit)="submit()" class="auth-form">
            <label>
              <span>Email</span>
              <input type="email" formControlName="email" placeholder="you@example.com" />
            </label>

            <label>
              <span>Пароль</span>
              <input type="password" formControlName="password" placeholder="Введите пароль" />
            </label>

            <p class="error" *ngIf="auth.error()">{{ auth.error() }}</p>

            <button type="submit" [disabled]="form.invalid || auth.loading()">
              {{ auth.loading() ? 'Проверяем доступ...' : 'Открыть панель' }}
            </button>
          </form>

          <p class="switch">
            Ещё нет аккаунта?
            <a routerLink="/register">Создать профиль</a>
          </p>
        </div>
      </section>
    </section>
  `,
  styles: [`
    :host {
      display: block;
    }

    .auth-layout {
      min-height: 100vh;
      width: min(1320px, calc(100% - 32px));
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 22px;
      padding: 20px 0;
      align-items: stretch;
    }

    .story-panel,
    .form-shell {
      position: relative;
      overflow: hidden;
      border-radius: 32px;
      border: 1px solid rgba(104, 72, 52, 0.12);
      box-shadow: 0 24px 60px rgba(40, 29, 21, 0.12);
      backdrop-filter: blur(16px);
    }

    .story-panel {
      padding: 32px;
      display: grid;
      align-content: space-between;
      gap: 22px;
      background:
        radial-gradient(circle at top right, rgba(228, 167, 88, 0.24), transparent 20rem),
        linear-gradient(135deg, rgba(61, 48, 38, 0.96), rgba(29, 24, 20, 0.96));
      color: #f9eedc;
    }

    .story-panel::after {
      content: '';
      position: absolute;
      inset: auto -4rem -5rem auto;
      width: 15rem;
      height: 15rem;
      border-radius: 50%;
      background: rgba(224, 163, 83, 0.18);
      filter: blur(18px);
    }

    .eyebrow,
    .form-kicker {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 0.78rem;
      font-weight: 700;
    }

    .eyebrow {
      color: rgba(255, 224, 182, 0.92);
    }

    h1,
    h2 {
      margin: 0;
      line-height: 0.96;
      letter-spacing: -0.04em;
    }

    h1 {
      font-size: clamp(2.8rem, 6vw, 5rem);
      max-width: 10ch;
    }

    .lead {
      margin: 0;
      max-width: 46ch;
      color: rgba(249, 238, 220, 0.82);
      font-size: 1rem;
      line-height: 1.65;
    }

    .story-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .story-grid article {
      padding: 16px;
      border-radius: 22px;
      background: rgba(255, 247, 234, 0.08);
      border: 1px solid rgba(255, 228, 192, 0.12);
      display: grid;
      gap: 8px;
    }

    .story-grid span {
      color: rgba(255, 210, 154, 0.92);
      font-size: 0.82rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .story-grid strong {
      font-size: 0.98rem;
      color: #fff3df;
    }

    .story-grid p {
      margin: 0;
      color: rgba(249, 238, 220, 0.72);
      line-height: 1.45;
      font-size: 0.92rem;
    }

    .form-panel {
      display: grid;
      align-items: center;
    }

    .form-shell {
      padding: 30px;
      background:
        radial-gradient(circle at top left, rgba(229, 175, 97, 0.18), transparent 18rem),
        linear-gradient(135deg, rgba(255, 251, 245, 0.95), rgba(246, 237, 224, 0.92));
      display: grid;
      gap: 16px;
    }

    .back-link {
      justify-self: start;
      display: inline-flex;
      align-items: center;
      text-decoration: none;
      color: #7b5a46;
      font-weight: 700;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255, 252, 247, 0.76);
      border: 1px solid rgba(104, 72, 52, 0.12);
    }

    .form-kicker {
      color: #a85c31;
    }

    h2 {
      font-size: clamp(2rem, 4vw, 3rem);
      color: #31231a;
    }

    .form-copy {
      margin: 0;
      color: #6b5b50;
      line-height: 1.55;
    }

    .auth-form {
      display: grid;
      gap: 14px;
    }

    label {
      display: grid;
      gap: 8px;
      color: #4f4138;
      font-weight: 700;
    }

    input {
      width: 100%;
      padding: 14px 15px;
      border-radius: 18px;
      border: 1px solid rgba(104, 72, 52, 0.16);
      background: rgba(255, 252, 247, 0.96);
      color: #261d17;
      transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
    }

    input:focus {
      outline: none;
      border-color: rgba(198, 107, 51, 0.6);
      box-shadow: 0 0 0 4px rgba(198, 107, 51, 0.12);
      transform: translateY(-1px);
    }

    button {
      border: 0;
      border-radius: 20px;
      padding: 14px 18px;
      font-weight: 700;
      color: #fff8f1;
      background: linear-gradient(135deg, #c96d37, #8f4527);
      cursor: pointer;
      box-shadow: 0 14px 24px rgba(143, 69, 39, 0.22);
    }

    button:disabled {
      opacity: 0.7;
      cursor: wait;
      box-shadow: none;
    }

    .error {
      margin: 0;
      color: #9d2933;
      font-weight: 700;
    }

    .switch {
      margin: 0;
      color: #6b5b50;
    }

    .switch a {
      color: #8f4527;
      font-weight: 700;
      text-decoration: none;
    }

    @media (max-width: 1100px) {
      .auth-layout,
      .story-grid {
        grid-template-columns: 1fr;
      }

      h1 {
        max-width: 11ch;
      }
    }

    @media (max-width: 720px) {
      .auth-layout {
        width: min(100% - 20px, 100%);
        padding: 18px 0;
      }

      .story-panel,
      .form-shell {
        padding: 22px;
      }
    }
  `],
})
export class LoginPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly router = inject(Router);

  readonly auth = inject(AuthService);

  readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  async submit(): Promise<void> {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    try {
      await this.auth.login(this.form.getRawValue());
      await this.router.navigateByUrl('/dashboard');
    } catch {
      // handled in auth service
    }
  }
}
