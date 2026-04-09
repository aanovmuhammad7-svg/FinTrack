import { computed, inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { environment } from '../../../environments/environment';
import { MessageResponse, TokenResponse, UserProfile } from '../models/api.models';
import { extractHttpErrorMessage } from '../utils/http-error.util';

interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface LoginPayload {
  email: string;
  password: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly baseUrl = environment.apiUrl;

  readonly user = signal<UserProfile | null>(null);
  readonly initialized = signal(false);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly isAuthenticated = computed(() => this.user() !== null);

  async bootstrap(): Promise<void> {
    if (this.initialized()) {
      return;
    }

    try {
      const profile = await firstValueFrom(
        this.http.get<UserProfile>(`${this.baseUrl}/users/profile`)
      );
      this.user.set(profile);
    } catch {
      this.user.set(null);
    } finally {
      this.initialized.set(true);
    }
  }

  async register(payload: RegisterPayload): Promise<MessageResponse> {
    this.loading.set(true);
    this.error.set(null);
    try {
      return await firstValueFrom(
        this.http.post<MessageResponse>(`${this.baseUrl}/auth/register`, payload)
      );
    } catch (error) {
      this.error.set(this.extractError(error));
      throw error;
    } finally {
      this.loading.set(false);
    }
  }

  async login(payload: LoginPayload): Promise<TokenResponse> {
    this.loading.set(true);
    this.error.set(null);
    try {
      const response = await firstValueFrom(
        this.http.post<TokenResponse>(`${this.baseUrl}/auth/login`, payload)
      );
      await this.refreshProfile();
      return response;
    } catch (error) {
      this.error.set(this.extractError(error));
      throw error;
    } finally {
      this.loading.set(false);
    }
  }

  async refreshProfile(): Promise<void> {
    const profile = await firstValueFrom(
      this.http.get<UserProfile>(`${this.baseUrl}/users/profile`)
    );
    this.user.set(profile);
  }

  async logout(): Promise<void> {
    try {
      await firstValueFrom(
        this.http.post<MessageResponse>(`${this.baseUrl}/auth/logout`, {})
      );
    } finally {
      this.user.set(null);
      await this.router.navigateByUrl('/login');
    }
  }

  private extractError(error: unknown): string {
    return extractHttpErrorMessage(error);
  }
}
