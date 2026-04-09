import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AnalyticsSummary,
  Budget,
  BudgetProgress,
  Category,
  ReportOverview,
  Transaction,
} from '../models/api.models';

interface CategoryPayload {
  name: string;
  type: 'income' | 'expense';
}

interface TransactionPayload {
  category_id: number;
  amount: number;
  description?: string;
  occurred_at?: string | null;
}

interface BudgetPayload {
  category_id: number;
  limit_amount: number;
  period_start: string;
  period_end: string;
}

@Injectable({ providedIn: 'root' })
export class FinanceService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  getCategories(): Promise<Category[]> {
    return firstValueFrom(this.http.get<Category[]>(`${this.baseUrl}/categories/`));
  }

  createCategory(payload: CategoryPayload): Promise<Category> {
    return firstValueFrom(this.http.post<Category>(`${this.baseUrl}/categories/`, payload));
  }

  getTransactions(): Promise<Transaction[]> {
    return firstValueFrom(this.http.get<Transaction[]>(`${this.baseUrl}/transactions/`));
  }

  createTransaction(payload: TransactionPayload): Promise<Transaction> {
    return firstValueFrom(
      this.http.post<Transaction>(`${this.baseUrl}/transactions/`, payload)
    );
  }

  getBudgets(): Promise<Budget[]> {
    return firstValueFrom(this.http.get<Budget[]>(`${this.baseUrl}/budgets/`));
  }

  getBudgetProgress(): Promise<BudgetProgress[]> {
    return firstValueFrom(this.http.get<BudgetProgress[]>(`${this.baseUrl}/budgets/progress`));
  }

  createBudget(payload: BudgetPayload): Promise<Budget> {
    return firstValueFrom(this.http.post<Budget>(`${this.baseUrl}/budgets/`, payload));
  }

  getAnalyticsSummary(): Promise<AnalyticsSummary> {
    return firstValueFrom(
      this.http.get<AnalyticsSummary>(`${this.baseUrl}/analytics/summary`)
    );
  }

  getReportOverview(dateFrom: string, dateTo: string): Promise<ReportOverview> {
    return firstValueFrom(
      this.http.get<ReportOverview>(`${this.baseUrl}/reports/overview`, {
        params: { date_from: dateFrom, date_to: dateTo },
      })
    );
  }
}
