import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <section class="auth-layout">
      <section class="form-panel">
        <div class="form-shell">
          <a class="back-link" routerLink="/">← На главную</a>
          <p class="form-kicker">Регистрация</p>
          <h1>Собрать новый профиль</h1>
          <p class="form-copy">
            Заполним только то, что реально нужно для старта: имя, фамилию, email и пароль.
          </p>

          <form [formGroup]="form" (ngSubmit)="submit()" class="auth-form">
            <div class="grid two">
              <label>
                <span>Имя</span>
                <input type="text" formControlName="first_name" placeholder="Айдана" />
              </label>

              <label>
                <span>Фамилия</span>
                <input type="text" formControlName="last_name" placeholder="Серик" />
              </label>
            </div>

            <label>
              <span>Email</span>
              <input type="email" formControlName="email" placeholder="you@example.com" />
            </label>

            <label>
              <span>Пароль</span>
              <input type="password" formControlName="password" placeholder="Минимум 8 символов" />
            </label>

            <p class="success" *ngIf="success()">{{ success() }}</p>
            <p class="error" *ngIf="auth.error()">{{ auth.error() }}</p>

            <button type="submit" [disabled]="form.invalid || auth.loading()">
              {{ auth.loading() ? 'Создаём профиль...' : 'Зарегистрироваться' }}
            </button>
          </form>

          <p class="switch">
            Уже есть аккаунт?
            <a routerLink="/login">Перейти ко входу</a>
          </p>
        </div>
      </section>

      <aside class="story-panel">
        <p class="eyebrow">Setup Flow</p>
        <h2>Новый старт без лишних полей.</h2>
        <p class="lead">
          Регистрация должна быть короткой. Всё, что не помогает сразу начать работу с приложением,
          лучше не спрашивать на первом шаге.
        </p>

        <div class="steps">
          <article>
            <strong>Быстрый вход</strong>
            <p>Меньше обязательных полей и меньше поводов бросить регистрацию.</p>
          </article>
          <article>
            <strong>Чистый профиль</strong>
            <p>Сначала только базовые данные, без перегруженной формы.</p>
          </article>
          <article>
            <strong>Сразу к работе</strong>
            <p>После регистрации можно переходить к категориям, операциям и бюджетам.</p>
          </article>
        </div>
      </aside>
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
      grid-template-columns: 0.95fr 0.88fr;
      gap: 18px;
      padding: 20px 0;
      align-items: stretch;
    }

    .form-shell,
    .story-panel {
      position: relative;
      overflow: hidden;
      border-radius: 32px;
      border: 1px solid rgba(104, 72, 52, 0.12);
      box-shadow: 0 24px 60px rgba(40, 29, 21, 0.12);
      backdrop-filter: blur(16px);
    }

    .form-shell {
      padding: 30px;
      background:
        radial-gradient(circle at top left, rgba(124, 147, 227, 0.16), transparent 18rem),
        radial-gradient(circle at bottom right, rgba(227, 170, 95, 0.16), transparent 18rem),
        linear-gradient(135deg, rgba(255, 251, 245, 0.95), rgba(246, 237, 224, 0.92));
      display: grid;
      gap: 16px;
    }

    .back-link {
      justify-self: start;
      display: inline-flex;
      align-items: center;
      text-decoration: none;
      color: #6350b3;
      font-weight: 700;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255, 252, 247, 0.76);
      border: 1px solid rgba(104, 72, 52, 0.12);
    }

    .story-panel {
      padding: 28px;
      display: grid;
      align-content: start;
      gap: 16px;
      background:
        radial-gradient(circle at top left, rgba(115, 143, 229, 0.22), transparent 20rem),
        linear-gradient(135deg, rgba(30, 35, 53, 0.96), rgba(25, 21, 33, 0.96));
      color: #f4f0ff;
      max-height: 680px;
    }

    .story-panel::after {
      content: '';
      position: absolute;
      inset: auto auto -4rem -3rem;
      width: 14rem;
      height: 14rem;
      border-radius: 50%;
      background: rgba(127, 153, 232, 0.18);
      filter: blur(20px);
    }

    .form-kicker,
    .eyebrow {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 0.78rem;
      font-weight: 700;
    }

    .form-kicker {
      color: #7b63c7;
    }

    .eyebrow {
      color: rgba(201, 210, 255, 0.9);
    }

    h1,
    h2 {
      margin: 0;
      letter-spacing: -0.04em;
      line-height: 0.96;
    }

    h1 {
      color: #2f231b;
      font-size: clamp(2.2rem, 4vw, 3.6rem);
    }

    h2 {
      color: #f4f0ff;
      font-size: clamp(2rem, 4.5vw, 3.7rem);
      max-width: 10ch;
    }

    .form-copy,
    .lead {
      margin: 0;
      line-height: 1.55;
    }

    .form-copy {
      color: #6b5b50;
    }

    .lead {
      color: rgba(244, 240, 255, 0.78);
      max-width: 40ch;
      font-size: 0.98rem;
    }

    .auth-form {
      display: grid;
      gap: 14px;
    }

    .grid {
      display: grid;
      gap: 16px;
    }

    .two {
      grid-template-columns: repeat(2, minmax(0, 1fr));
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
      border-color: rgba(123, 99, 199, 0.58);
      box-shadow: 0 0 0 4px rgba(123, 99, 199, 0.12);
      transform: translateY(-1px);
    }

    button {
      border: 0;
      border-radius: 20px;
      padding: 14px 18px;
      font-weight: 700;
      color: #fff9ff;
      background: linear-gradient(135deg, #7d66cb, #4b5fb8);
      cursor: pointer;
      box-shadow: 0 14px 24px rgba(75, 95, 184, 0.22);
    }

    button:disabled {
      opacity: 0.7;
      cursor: wait;
      box-shadow: none;
    }

    .error,
    .success {
      margin: 0;
      font-weight: 700;
    }

    .error {
      color: #9d2933;
    }

    .success {
      color: #2f7a4f;
    }

    .switch {
      margin: 0;
      color: #6b5b50;
    }

    .steps {
      display: grid;
      gap: 10px;
      margin-top: 4px;
    }

    .steps article {
      padding: 14px 16px;
      border-radius: 20px;
      background: rgba(245, 241, 255, 0.08);
      border: 1px solid rgba(214, 220, 255, 0.12);
      display: grid;
      gap: 6px;
    }

    .steps strong {
      color: #ffffff;
      font-size: 0.98rem;
    }

    .steps p {
      margin: 0;
      color: rgba(244, 240, 255, 0.74);
      line-height: 1.45;
      font-size: 0.92rem;
    }

    .switch a {
      color: #6350b3;
      font-weight: 700;
      text-decoration: none;
    }

    @media (max-width: 1100px) {
      .auth-layout,
      .two {
        grid-template-columns: 1fr;
      }

      .story-panel {
        max-height: none;
      }

      h2 {
        max-width: 12ch;
      }
    }

    @media (max-width: 720px) {
      .auth-layout {
        width: min(100% - 20px, 100%);
        padding: 18px 0;
      }

      .form-shell,
      .story-panel {
        padding: 22px;
      }
    }
  `],
})
export class RegisterPageComponent {
  private readonly fb = inject(FormBuilder);

  readonly auth = inject(AuthService);
  readonly success = signal('');

  readonly form = this.fb.nonNullable.group({
    first_name: ['', [Validators.required]],
    last_name: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  async submit(): Promise<void> {
    this.success.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    try {
      const response = await this.auth.register(this.form.getRawValue());
      this.success.set(response.message);
      this.form.reset({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
      });
    } catch {
      // handled in auth service
    }
  }
}
