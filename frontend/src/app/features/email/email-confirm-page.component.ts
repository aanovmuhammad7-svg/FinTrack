import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { EmailService } from '../../core/services/email.service';
import { extractHttpErrorMessage } from '../../core/utils/http-error.util';

@Component({
  selector: 'app-email-confirm-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <section class="confirm-layout">
      <div class="confirm-card">
        <p class="eyebrow">Email Confirmation</p>

        <ng-container [ngSwitch]="state()">
          <div *ngSwitchCase="'loading'" class="state">
            <h1>Подтверждаем email</h1>
            <p>Проверяем ссылку и завершаем активацию аккаунта.</p>
          </div>

          <div *ngSwitchCase="'success'" class="state">
            <h1>Email подтверждён</h1>
            <p>{{ message() }}</p>
            <div class="actions">
              <a class="primary" routerLink="/login">Перейти ко входу</a>
              <a class="secondary" routerLink="/">На главную</a>
            </div>
          </div>

          <div *ngSwitchCase="'error'" class="state">
            <h1>Не удалось подтвердить email</h1>
            <p>{{ message() }}</p>
            <div class="actions">
              <a class="primary" routerLink="/register">К регистрации</a>
              <a class="secondary" routerLink="/">На главную</a>
            </div>
          </div>
        </ng-container>
      </div>
    </section>
  `,
  styles: [`
    :host {
      display: block;
    }

    .confirm-layout {
      min-height: 100vh;
      width: min(880px, calc(100% - 24px));
      margin: 0 auto;
      display: grid;
      place-items: center;
      padding: 24px 0;
    }

    .confirm-card {
      width: min(100%, 620px);
      padding: 34px;
      border-radius: 32px;
      border: 1px solid rgba(104, 72, 52, 0.12);
      background:
        radial-gradient(circle at top left, rgba(228, 167, 88, 0.18), transparent 18rem),
        linear-gradient(135deg, rgba(255, 251, 245, 0.96), rgba(246, 237, 224, 0.92));
      box-shadow: 0 24px 60px rgba(40, 29, 21, 0.12);
      display: grid;
      gap: 18px;
    }

    .eyebrow {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 0.78rem;
      font-weight: 700;
      color: #a85c31;
    }

    .state {
      display: grid;
      gap: 14px;
    }

    h1 {
      margin: 0;
      color: #2f231b;
      font-size: clamp(2.2rem, 5vw, 3.4rem);
      line-height: 0.96;
      letter-spacing: -0.04em;
    }

    p {
      margin: 0;
      color: #6b5b50;
      line-height: 1.6;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 6px;
    }

    .primary,
    .secondary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      font-weight: 700;
      border-radius: 999px;
      padding: 14px 20px;
    }

    .primary {
      color: #fff8f1;
      background: linear-gradient(135deg, #c96d37, #8f4527);
      box-shadow: 0 14px 24px rgba(143, 69, 39, 0.22);
    }

    .secondary {
      color: #5d4b40;
      background: rgba(255, 252, 247, 0.9);
      border: 1px solid rgba(104, 72, 52, 0.12);
    }
  `],
})
export class EmailConfirmPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly emailService = inject(EmailService);

  readonly state = signal<'loading' | 'success' | 'error'>('loading');
  readonly message = signal('Подождите пару секунд.');

  constructor() {
    void this.confirm();
  }

  private async confirm(): Promise<void> {
    const email = this.route.snapshot.queryParamMap.get('email');
    const token = this.route.snapshot.queryParamMap.get('token');

    if (!email || !token) {
      this.state.set('error');
      this.message.set('Ссылка подтверждения неполная или повреждена.');
      return;
    }

    try {
      const response = await this.emailService.confirmEmail({
        email,
        confirmation_token: token,
      });
      this.state.set('success');
      this.message.set(response.message);
    } catch (error) {
      this.state.set('error');
      this.message.set(extractHttpErrorMessage(error));
    }
  }
}
