export interface MessageResponse {
  message: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  first_name: string;
  last_name: string;
  email: string;
  birthday: string | null;
  email_confirmed: boolean;
  created_at: string;
}

export interface Category {
  id: number;
  user_id: number;
  name: string;
  type: 'income' | 'expense';
}

export interface Transaction {
  id: number;
  user_id: number;
  category_id: number;
  amount: string;
  description: string | null;
  occurred_at: string | null;
  created_at: string;
}

export interface Budget {
  id: number;
  user_id: number;
  category_id: number;
  limit_amount: string;
  period_start: string;
  period_end: string;
  is_active: boolean;
  created_at: string;
}

export interface BudgetProgress {
  budget_id: number;
  category_id: number;
  category_name: string;
  limit_amount: string;
  spent_amount: string;
  remaining_amount: string;
  utilization_percent: number;
  period_start: string;
  period_end: string;
  is_active: boolean;
}

export interface AnalyticsSummary {
  income: string;
  expense: string;
  balance: string;
}

export interface ReportCategoryItem {
  category_id: number;
  category_name: string;
  category_type: string;
  total: string;
}

export interface ReportDailyItem {
  day: string;
  income: string;
  expense: string;
  balance: string;
}

export interface ReportBudgetItem {
  budget_id: number;
  category_id: number;
  category_name: string;
  limit_amount: string;
  spent_amount: string;
  remaining_amount: string;
  utilization_percent: number;
  period_start: string;
  period_end: string;
}

export interface ReportOverview {
  summary: {
    date_from: string;
    date_to: string;
    income: string;
    expense: string;
    balance: string;
  };
  by_category: ReportCategoryItem[];
  daily: ReportDailyItem[];
  budgets: ReportBudgetItem[];
}
