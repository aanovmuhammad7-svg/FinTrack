import { HttpErrorResponse } from '@angular/common/http';

export function extractHttpErrorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (typeof error.error?.detail === 'string') {
      return error.error.detail;
    }
    if (typeof error.error?.message === 'string') {
      return error.error.message;
    }
    if (typeof error.error?.error === 'string') {
      return error.error.error;
    }
    if (typeof error.message === 'string' && error.message) {
      return error.message;
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return 'Не удалось выполнить запрос.';
}
