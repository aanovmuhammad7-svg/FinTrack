import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { LandingPageComponent } from './features/landing/landing-page.component';
import { LoginPageComponent } from './features/auth/login-page.component';
import { RegisterPageComponent } from './features/auth/register-page.component';
import { DashboardPageComponent } from './features/dashboard/dashboard-page.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', component: LandingPageComponent },
  { path: 'login', component: LoginPageComponent },
  { path: 'register', component: RegisterPageComponent },
  { path: 'dashboard', component: DashboardPageComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '' },
];
