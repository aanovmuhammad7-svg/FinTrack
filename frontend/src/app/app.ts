import { CommonModule } from '@angular/common';
import { Component, HostListener, computed, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';

import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  readonly currentUrl = signal(this.router.url);
  readonly scrollY = signal(typeof window !== 'undefined' ? window.scrollY : 0);

  readonly showTopbar = computed(() => {
    const url = this.currentUrl();
    return url !== '/login' && url !== '/register' && url !== '/email/confirm';
  });

  readonly hideTopbarOnLandingScroll = computed(
    () => this.currentUrl() === '/' && this.scrollY() > 48,
  );

  constructor() {
    void this.authService.bootstrap();

    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => {
        this.currentUrl.set(this.router.url);
      });
  }

  @HostListener('window:scroll')
  onWindowScroll(): void {
    this.scrollY.set(window.scrollY);
  }

  async logout(): Promise<void> {
    await this.authService.logout();
  }
}
