import { HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';

function readCookie(name: string): string | null {
  const escaped = name.replace(/[-[\]/{}()*+?.\\^$|]/g, '\\$&');
  const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export const apiInterceptor: HttpInterceptorFn = (request: HttpRequest<unknown>, next: HttpHandlerFn) => {
  let nextRequest = request.clone({ withCredentials: true });

  if (['POST', 'PATCH', 'PUT', 'DELETE'].includes(request.method.toUpperCase())) {
    const csrfToken = readCookie('csrf_token');
    if (csrfToken) {
      nextRequest = nextRequest.clone({
        setHeaders: {
          'X-CSRF-Token': csrfToken,
        },
      });
    }
  }

  return next(nextRequest);
};
