import { CommonModule, CurrencyPipe, DatePipe, DecimalPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Budget, BudgetProgress, Category, ReportOverview, Transaction } from '../../core/models/api.models';
import { AuthService } from '../../core/services/auth.service';
import { FinanceService } from '../../core/services/finance.service';
import { extractHttpErrorMessage } from '../../core/utils/http-error.util';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CurrencyPipe, DatePipe, DecimalPipe],
  template: `
    <section class="dashboard">
      <header class="hero panel">
        <div class="hero-copy">
          <p class="eyebrow">FinTrack Control Room</p>
          <h1>Финансовая картина без хаоса</h1>
          <p class="subtitle" *ngIf="auth.user() as user">
            {{ user.first_name }}, здесь собраны ваши категории, движение денег, бюджеты и отчёты в одном рабочем пространстве.
          </p>
        </div>

        <div class="hero-actions">
          <div class="status-tile">
            <span class="status-dot"></span>
            <span>Данные синхронизированы с backend</span>
          </div>
          <button class="ghost" type="button" (click)="logout()">Выйти</button>
        </div>
      </header>

      <p class="notice" *ngIf="notice()">{{ notice() }}</p>
      <p class="loading-banner" *ngIf="pageLoading()">Обновляем данные панели...</p>

      <section class="summary-grid" *ngIf="summary() as currentSummary">
        <article class="summary-card income">
          <span class="label">Доходы</span>
          <strong>{{ currentSummary.income | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
          <small>Все входящие операции за выбранный период</small>
        </article>

        <article class="summary-card expense">
          <span class="label">Расходы</span>
          <strong>{{ currentSummary.expense | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
          <small>Все списания по категориям расходов</small>
        </article>

        <article class="summary-card balance">
          <span class="label">Баланс</span>
          <strong>{{ currentSummary.balance | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
          <small>Текущий чистый результат</small>
        </article>
      </section>

      <section class="workspace-grid">
        <article class="panel form-panel accent-amber">
          <div class="panel-head">
            <div>
              <p class="section-tag">Быстрое действие</p>
              <h2>Новая категория</h2>
            </div>
            <span>{{ categories().length }} всего</span>
          </div>

          <form [formGroup]="categoryForm" (ngSubmit)="createCategory()" class="stack">
            <label>
              <span>Название</span>
              <input type="text" formControlName="name" placeholder="Например: Кафе, Такси, Фриланс" />
            </label>

            <label>
              <span>Тип</span>
              <select formControlName="type">
                <option value="expense">expense</option>
                <option value="income">income</option>
              </select>
            </label>

            <button type="submit" [disabled]="categoryForm.invalid || pageLoading()">Создать категорию</button>
          </form>
        </article>

        <article class="panel form-panel accent-green">
          <div class="panel-head">
            <div>
              <p class="section-tag">Поток денег</p>
              <h2>Новая транзакция</h2>
            </div>
            <span>{{ transactions().length }} операций</span>
          </div>

          <form [formGroup]="transactionForm" (ngSubmit)="createTransaction()" class="stack">
            <label>
              <span>Категория</span>
              <select formControlName="category_id">
                <option value="">Выберите категорию</option>
                <option *ngFor="let category of categories()" [value]="category.id">
                  {{ category.name }} · {{ category.type }}
                </option>
              </select>
            </label>

            <label>
              <span>Сумма</span>
              <input type="number" formControlName="amount" min="0" step="0.01" placeholder="0.00" />
            </label>

            <label>
              <span>Описание</span>
              <input type="text" formControlName="description" placeholder="Короткая заметка о платеже" />
            </label>

            <label>
              <span>Дата и время</span>
              <input type="datetime-local" formControlName="occurred_at" />
            </label>

            <button type="submit" [disabled]="transactionForm.invalid || pageLoading()">Сохранить транзакцию</button>
          </form>
        </article>

        <article class="panel form-panel accent-blue">
          <div class="panel-head">
            <div>
              <p class="section-tag">Контроль расходов</p>
              <h2>Новый бюджет</h2>
            </div>
            <span>{{ budgets().length }} бюджетов</span>
          </div>

          <form [formGroup]="budgetForm" (ngSubmit)="createBudget()" class="stack">
            <label>
              <span>Категория расходов</span>
              <select formControlName="category_id">
                <option value="">Выберите категорию</option>
                <option *ngFor="let category of expenseCategories()" [value]="category.id">
                  {{ category.name }}
                </option>
              </select>
            </label>

            <label>
              <span>Лимит</span>
              <input type="number" formControlName="limit_amount" min="0" step="0.01" placeholder="0.00" />
            </label>

            <div class="date-grid">
              <label>
                <span>Начало периода</span>
                <input type="date" formControlName="period_start" />
              </label>

              <label>
                <span>Конец периода</span>
                <input type="date" formControlName="period_end" />
              </label>
            </div>

            <button type="submit" [disabled]="budgetForm.invalid || pageLoading()">Сохранить бюджет</button>
          </form>
        </article>
      </section>

      <section class="two-column">
        <article class="panel category-showcase">
          <div class="panel-head">
            <div>
              <p class="section-tag">Структура</p>
              <h2>Категории</h2>
            </div>
            <span>Доходы и расходы</span>
          </div>

          <div class="chips">
            <span class="chip" [class.income-chip]="category.type === 'income'" *ngFor="let category of categories()">
              <span class="chip-name">{{ category.name }}</span>
              <span class="chip-type">{{ category.type }}</span>
            </span>
          </div>
        </article>

        <article class="panel report-hero" *ngIf="report() as currentReport">
          <div class="panel-head">
            <div>
              <p class="section-tag">Отчёт</p>
              <h2>Период {{ currentReport.summary.date_from }} - {{ currentReport.summary.date_to }}</h2>
            </div>
            <span>{{ currentReport.daily.length }} дневных срезов</span>
          </div>

          <div class="report-highlights">
            <div>
              <span>Доход</span>
              <strong>{{ currentReport.summary.income | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
            </div>
            <div>
              <span>Расход</span>
              <strong>{{ currentReport.summary.expense | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
            </div>
            <div>
              <span>Итог</span>
              <strong>{{ currentReport.summary.balance | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
            </div>
          </div>
        </article>
      </section>

      <section class="two-column">
        <article class="panel ledger-panel">
          <div class="panel-head">
            <div>
              <p class="section-tag">История</p>
              <h2>Последние транзакции</h2>
            </div>
            <span>{{ transactions().length }} записей</span>
          </div>

          <div class="ledger-list" *ngIf="transactions().length; else emptyTransactions">
            <article class="ledger-item" *ngFor="let tx of transactions()">
              <div class="ledger-main">
                <strong>{{ categoryName(tx.category_id) }}</strong>
                <span>{{ tx.description || 'Без описания' }}</span>
              </div>
              <div class="ledger-meta">
                <span>{{ tx.occurred_at | date:'dd.MM.yyyy HH:mm' }}</span>
                <strong>{{ tx.amount | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
              </div>
            </article>
          </div>

          <ng-template #emptyTransactions>
            <p class="empty">Пока нет транзакций. Добавьте первую операцию из верхнего блока.</p>
          </ng-template>
        </article>

        <article class="panel budget-panel">
          <div class="panel-head">
            <div>
              <p class="section-tag">Лимиты</p>
              <h2>Прогресс бюджетов</h2>
            </div>
            <span>{{ budgetProgress().length }} активных</span>
          </div>

          <div class="budget-list" *ngIf="budgetProgress().length; else emptyBudgets">
            <div class="budget-card" *ngFor="let budget of budgetProgress()">
              <div class="budget-meta">
                <strong>{{ budget.category_name }}</strong>
                <span>{{ budget.spent_amount | currency:'KZT':'symbol-narrow':'1.0-2' }} / {{ budget.limit_amount | currency:'KZT':'symbol-narrow':'1.0-2' }}</span>
              </div>

              <div class="bar">
                <div class="fill" [style.width.%]="budget.utilization_percent > 100 ? 100 : budget.utilization_percent"></div>
              </div>

              <div class="budget-foot">
                <span>Осталось {{ budget.remaining_amount | currency:'KZT':'symbol-narrow':'1.0-2' }}</span>
                <span>{{ budget.utilization_percent | number:'1.0-2' }}%</span>
              </div>
            </div>
          </div>

          <ng-template #emptyBudgets>
            <p class="empty">Пока нет бюджетов. Создайте лимит, и система начнёт считать прогресс автоматически.</p>
          </ng-template>
        </article>
      </section>

      <section class="panel report-panel">
        <div class="panel-head">
          <div>
            <p class="section-tag">Детальный обзор</p>
            <h2>Отчёт по периоду</h2>
          </div>
          <span>Summary + categories + daily + budgets</span>
        </div>

        <form [formGroup]="reportForm" (ngSubmit)="loadReport()" class="report-form">
          <label>
            <span>Дата с</span>
            <input type="date" formControlName="date_from" />
          </label>
          <label>
            <span>Дата по</span>
            <input type="date" formControlName="date_to" />
          </label>
          <button type="submit" [disabled]="reportForm.invalid || pageLoading()">Обновить отчёт</button>
        </form>

        <div *ngIf="report() as currentReport" class="report-grid">
          <div class="report-section">
            <h3>По категориям</h3>
            <ul>
              <li *ngFor="let item of currentReport.by_category">
                <span>{{ item.category_name }} · {{ item.category_type }}</span>
                <strong>{{ item.total | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
              </li>
            </ul>
          </div>

          <div class="report-section">
            <h3>По дням</h3>
            <ul>
              <li *ngFor="let item of currentReport.daily">
                <span>{{ item.day }}</span>
                <strong>{{ item.balance | currency:'KZT':'symbol-narrow':'1.0-2' }}</strong>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </section>
  `,
  styles: [`
    :host {
      display: block;
    }

    .dashboard {
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
      display: grid;
      gap: 22px;
    }

    .panel {
      position: relative;
      overflow: hidden;
      padding: 24px;
      border-radius: 28px;
      border: 1px solid rgba(104, 72, 52, 0.12);
      background:
        linear-gradient(135deg, rgba(255, 251, 245, 0.92), rgba(246, 237, 224, 0.9)),
        rgba(248, 243, 232, 0.88);
      box-shadow: 0 24px 60px rgba(40, 29, 21, 0.12);
      backdrop-filter: blur(16px);
    }

    .panel::after {
      content: '';
      position: absolute;
      inset: auto -6% -36% auto;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(214, 162, 90, 0.14), transparent 70%);
      pointer-events: none;
    }

    .hero,
    .summary-grid,
    .workspace-grid,
    .two-column {
      display: grid;
      gap: 22px;
    }

    .hero {
      grid-template-columns: 1.3fr 0.7fr;
      align-items: center;
      padding: 32px;
    }

    .hero-copy {
      display: grid;
      gap: 12px;
      max-width: 700px;
    }

    .hero-actions {
      display: grid;
      gap: 14px;
      justify-items: end;
    }

    .eyebrow,
    .section-tag {
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.76rem;
      color: #aa5d31;
    }

    h1 {
      margin: 0;
      font-size: clamp(2.6rem, 6vw, 5rem);
      line-height: 0.95;
      color: #2f2219;
    }

    h2,
    h3 {
      margin: 0;
      color: #33251c;
      letter-spacing: -0.02em;
    }

    .subtitle {
      margin: 0;
      max-width: 60ch;
      font-size: 1.02rem;
      line-height: 1.6;
      color: #67564d;
    }

    .status-tile {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 14px;
      border-radius: 999px;
      background: rgba(247, 252, 244, 0.95);
      border: 1px solid rgba(83, 134, 96, 0.16);
      color: #365d41;
      font-weight: 600;
    }

    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #4a9b61;
      box-shadow: 0 0 0 6px rgba(74, 155, 97, 0.15);
    }

    .notice,
    .loading-banner {
      margin: 0;
      padding: 14px 18px;
      border-radius: 18px;
      font-weight: 600;
    }

    .notice {
      border: 1px solid rgba(204, 129, 79, 0.18);
      background: rgba(255, 245, 224, 0.78);
      color: #6d5544;
    }

    .loading-banner {
      border: 1px solid rgba(92, 117, 214, 0.16);
      background: rgba(232, 239, 255, 0.78);
      color: #42568d;
    }

    .summary-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .summary-card {
      padding: 24px;
      border-radius: 28px;
      display: grid;
      gap: 8px;
      color: #2f241d;
      box-shadow: 0 20px 40px rgba(40, 29, 21, 0.1);
    }

    .summary-card .label {
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: rgba(47, 36, 29, 0.68);
    }

    .summary-card strong {
      font-size: clamp(1.6rem, 3vw, 2.2rem);
      line-height: 1;
    }

    .summary-card small {
      color: rgba(47, 36, 29, 0.68);
    }

    .income {
      background: linear-gradient(135deg, #dff3e4, #eef8e8);
    }

    .expense {
      background: linear-gradient(135deg, #f9ddd2, #faebdf);
    }

    .balance {
      background: linear-gradient(135deg, #e2e7fb, #edf1ff);
    }

    .workspace-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .form-panel {
      display: grid;
      gap: 18px;
    }

    .accent-amber::before,
    .accent-green::before,
    .accent-blue::before {
      content: '';
      position: absolute;
      inset: 0 auto 0 0;
      width: 6px;
      border-radius: 28px 0 0 28px;
    }

    .accent-amber::before { background: linear-gradient(180deg, #c76430, #e3a14b); }
    .accent-green::before { background: linear-gradient(180deg, #3e8f60, #88c97a); }
    .accent-blue::before { background: linear-gradient(180deg, #5d77d1, #84b5ea); }

    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
    }

    .panel-head span {
      color: #6f5f56;
      font-size: 0.92rem;
    }

    .stack,
    .report-form {
      display: grid;
      gap: 14px;
    }

    .date-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    label {
      display: grid;
      gap: 8px;
      color: #55463d;
      font-weight: 600;
    }

    label span {
      font-size: 0.92rem;
    }

    input,
    select,
    button {
      font: inherit;
    }

    input,
    select {
      width: 100%;
      padding: 13px 14px;
      border-radius: 16px;
      border: 1px solid rgba(104, 72, 52, 0.16);
      background: rgba(255, 252, 247, 0.94);
      color: #241b16;
      transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
    }

    input:focus,
    select:focus {
      outline: none;
      border-color: rgba(198, 107, 51, 0.6);
      box-shadow: 0 0 0 4px rgba(198, 107, 51, 0.12);
      transform: translateY(-1px);
    }

    button {
      border: 0;
      border-radius: 18px;
      padding: 13px 16px;
      font-weight: 700;
      cursor: pointer;
      color: #fff8f1;
      background: linear-gradient(135deg, #c86834, #964525);
      box-shadow: 0 12px 22px rgba(151, 69, 37, 0.22);
      transition: transform 180ms ease, box-shadow 180ms ease;
    }

    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 16px 28px rgba(151, 69, 37, 0.26);
    }

    button:disabled {
      opacity: 0.7;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .ghost {
      color: #623a1f;
      background: rgba(248, 243, 232, 0.85);
      border: 1px solid rgba(104, 72, 52, 0.14);
      box-shadow: none;
    }

    .category-showcase,
    .report-hero {
      min-height: 220px;
    }

    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .chip {
      display: inline-grid;
      gap: 4px;
      padding: 12px 14px;
      border-radius: 18px;
      background: rgba(255, 249, 239, 0.92);
      border: 1px solid rgba(104, 72, 52, 0.1);
    }

    .income-chip {
      background: rgba(237, 250, 238, 0.94);
    }

    .chip-name {
      font-weight: 700;
      color: #35271f;
    }

    .chip-type {
      color: #78675b;
      font-size: 0.88rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .report-highlights {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: auto;
    }

    .report-highlights div {
      padding: 16px;
      border-radius: 18px;
      background: rgba(255, 250, 244, 0.82);
      border: 1px solid rgba(104, 72, 52, 0.08);
      display: grid;
      gap: 8px;
    }

    .report-highlights span {
      color: #75655c;
      font-size: 0.88rem;
    }

    .report-highlights strong {
      font-size: 1.2rem;
      color: #31231a;
    }

    .two-column {
      grid-template-columns: 1.15fr 0.85fr;
    }

    .ledger-list,
    .budget-list {
      display: grid;
      gap: 14px;
    }

    .ledger-item,
    .budget-card {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 18px;
      border-radius: 20px;
      background: rgba(255, 250, 242, 0.92);
      border: 1px solid rgba(104, 72, 52, 0.08);
    }

    .ledger-main,
    .ledger-meta {
      display: grid;
      gap: 6px;
    }

    .ledger-main strong,
    .budget-meta strong {
      color: #32251d;
    }

    .ledger-main span,
    .ledger-meta span,
    .budget-meta span,
    .budget-foot {
      color: #6e5e54;
    }

    .ledger-meta {
      justify-items: end;
      text-align: right;
    }

    .budget-card {
      display: grid;
    }

    .budget-meta,
    .budget-foot {
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }

    .bar {
      width: 100%;
      height: 12px;
      border-radius: 999px;
      background: rgba(205, 190, 174, 0.42);
      overflow: hidden;
    }

    .fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #ca6d36, #e3a249);
    }

    .empty {
      margin: 0;
      padding: 18px;
      border-radius: 18px;
      background: rgba(255, 251, 246, 0.85);
      color: #736359;
      border: 1px dashed rgba(104, 72, 52, 0.16);
    }

    .report-panel {
      display: grid;
      gap: 18px;
    }

    .report-form {
      grid-template-columns: 1fr 1fr auto;
      align-items: end;
    }

    .report-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }

    .report-section {
      padding: 18px;
      border-radius: 22px;
      background: rgba(255, 251, 246, 0.8);
      border: 1px solid rgba(104, 72, 52, 0.08);
    }

    ul {
      list-style: none;
      margin: 14px 0 0;
      padding: 0;
      display: grid;
      gap: 12px;
    }

    li {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(104, 72, 52, 0.08);
    }

    li:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }

    @media (max-width: 1100px) {
      .hero,
      .workspace-grid,
      .summary-grid,
      .two-column,
      .report-grid,
      .report-highlights,
      .report-form {
        grid-template-columns: 1fr;
      }

      .hero-actions {
        justify-items: start;
      }
    }

    @media (max-width: 720px) {
      .dashboard {
        width: min(100% - 20px, 100%);
        padding-top: 20px;
      }

      .panel,
      .hero {
        padding: 20px;
      }

      .date-grid,
      .budget-meta,
      .budget-foot,
      .panel-head,
      li,
      .ledger-item {
        grid-template-columns: 1fr;
        flex-direction: column;
        align-items: flex-start;
      }

      .ledger-meta {
        justify-items: start;
        text-align: left;
      }
    }
  `],
})
export class DashboardPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly finance = inject(FinanceService);

  readonly auth = inject(AuthService);
  readonly categories = signal<Category[]>([]);
  readonly transactions = signal<Transaction[]>([]);
  readonly budgets = signal<Budget[]>([]);
  readonly budgetProgress = signal<BudgetProgress[]>([]);
  readonly report = signal<ReportOverview | null>(null);
  readonly summary = signal<{ income: string; expense: string; balance: string } | null>(null);
  readonly notice = signal('');
  readonly pageLoading = signal(false);

  readonly expenseCategories = computed(() =>
    this.categories().filter((category) => category.type === 'expense'),
  );

  readonly categoryForm = this.fb.nonNullable.group({
    name: ['', [Validators.required]],
    type: ['expense' as 'expense' | 'income', [Validators.required]],
  });

  readonly transactionForm = this.fb.nonNullable.group({
    category_id: ['', [Validators.required]],
    amount: ['', [Validators.required]],
    description: [''],
    occurred_at: [this.currentDateTimeLocal(), [Validators.required]],
  });

  readonly budgetForm = this.fb.nonNullable.group({
    category_id: ['', [Validators.required]],
    limit_amount: ['', [Validators.required]],
    period_start: [this.currentMonthStart(), [Validators.required]],
    period_end: [this.currentMonthEnd(), [Validators.required]],
  });

  readonly reportForm = this.fb.nonNullable.group({
    date_from: [this.currentMonthStart(), [Validators.required]],
    date_to: [this.currentMonthEnd(), [Validators.required]],
  });

  constructor() {
    void this.loadAll();
  }

  async logout(): Promise<void> {
    await this.auth.logout();
  }

  async createCategory(): Promise<void> {
    if (this.categoryForm.invalid) {
      return;
    }

    try {
      await this.finance.createCategory(this.categoryForm.getRawValue());
      this.categoryForm.reset({ name: '', type: 'expense' });
      this.notice.set('Категория сохранена.');
      await this.loadCategories();
    } catch (error) {
      this.notice.set(this.toMessage(error));
    }
  }

  async createTransaction(): Promise<void> {
    if (this.transactionForm.invalid) {
      return;
    }

    const raw = this.transactionForm.getRawValue();

    try {
      await this.finance.createTransaction({
        category_id: Number(raw.category_id),
        amount: Number(raw.amount),
        description: raw.description,
        occurred_at: new Date(raw.occurred_at).toISOString(),
      });
      this.transactionForm.patchValue({
        amount: '',
        description: '',
        occurred_at: this.currentDateTimeLocal(),
      });
      this.notice.set('Транзакция сохранена.');
      await this.loadAll();
    } catch (error) {
      this.notice.set(this.toMessage(error));
    }
  }

  async createBudget(): Promise<void> {
    if (this.budgetForm.invalid) {
      return;
    }

    const raw = this.budgetForm.getRawValue();

    try {
      await this.finance.createBudget({
        category_id: Number(raw.category_id),
        limit_amount: Number(raw.limit_amount),
        period_start: raw.period_start,
        period_end: raw.period_end,
      });
      this.notice.set('Бюджет сохранён.');
      await this.loadBudgets();
      await this.loadReport();
    } catch (error) {
      this.notice.set(this.toMessage(error));
    }
  }

  async loadReport(): Promise<void> {
    if (this.reportForm.invalid) {
      return;
    }

    const { date_from, date_to } = this.reportForm.getRawValue();

    try {
      this.report.set(await this.finance.getReportOverview(date_from, date_to));
    } catch (error) {
      this.notice.set(this.toMessage(error));
    }
  }

  categoryName(categoryId: number): string {
    return this.categories().find((item) => item.id === categoryId)?.name ?? `#${categoryId}`;
  }

  private async loadAll(): Promise<void> {
    this.pageLoading.set(true);
    try {
      await Promise.all([
        this.loadCategories(),
        this.loadTransactions(),
        this.loadBudgets(),
        this.loadSummary(),
        this.loadReport(),
      ]);
    } catch (error) {
      this.notice.set(this.toMessage(error));
    } finally {
      this.pageLoading.set(false);
    }
  }

  private async loadCategories(): Promise<void> {
    this.categories.set(await this.finance.getCategories());
  }

  private async loadTransactions(): Promise<void> {
    this.transactions.set(await this.finance.getTransactions());
  }

  private async loadBudgets(): Promise<void> {
    const [budgets, progress] = await Promise.all([
      this.finance.getBudgets(),
      this.finance.getBudgetProgress(),
    ]);
    this.budgets.set(budgets);
    this.budgetProgress.set(progress);
  }

  private async loadSummary(): Promise<void> {
    this.summary.set(await this.finance.getAnalyticsSummary());
  }

  private currentMonthStart(): string {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
  }

  private currentMonthEnd(): string {
    const now = new Date();
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    return `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
  }

  private currentDateTimeLocal(): string {
    const now = new Date();
    const offset = now.getTimezoneOffset();
    const local = new Date(now.getTime() - offset * 60_000);
    return local.toISOString().slice(0, 16);
  }

  private toMessage(error: unknown): string {
    return extractHttpErrorMessage(error);
  }
}
