import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { environment } from '../../../environments/environment';
import { MessageResponse } from '../models/api.models';

interface ConfirmEmailPayload {
  email: string;
  confirmation_token: string;
}

interface ResendEmailPayload {
  email: string;
}

@Injectable({ providedIn: 'root' })
export class EmailService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  confirmEmail(payload: ConfirmEmailPayload): Promise<MessageResponse> {
    return firstValueFrom(
      this.http.post<MessageResponse>(`${this.baseUrl}/email/confirm`, payload),
    );
  }

  resendConfirmation(payload: ResendEmailPayload): Promise<MessageResponse> {
    return firstValueFrom(
      this.http.post<MessageResponse>(`${this.baseUrl}/email/resend`, payload),
    );
  }
}
