import { Injectable, Inject, Optional } from '@angular/core';

export const APP_CONFIG_TOKEN = 'APP_CONFIG';

export interface AppConfig {
  apiUrl: string;
  debug?: boolean;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

@Injectable({ providedIn: 'root' })
export class EnvironmentService {
  private readonly config: AppConfig;

  constructor(@Optional() @Inject(APP_CONFIG_TOKEN) config?: AppConfig) {
    this.config = config || this.getDefaultConfig();
  }

  private getDefaultConfig(): AppConfig {
    const isDev = this.isDevelopment();
    const isProduction = this.isProduction();

    let apiUrl: string;

    if (isDev) {
      // Development: point to ngrok backend
      apiUrl = 'https://powdering-junction-verbally.ngrok-free.dev/api';
    } else if (isProduction) {
      // Production: use relative path (proxied by nginx/server)
      apiUrl = '/api';
    } else {
      // Staging/other: use backend's full domain
      apiUrl = `http://${window.location.hostname}:8080/api`;
    }

    return {
      apiUrl,
      debug: isDev,
      logLevel: isDev ? 'debug' : 'warn'
    };
  }

  private isDevelopment(): boolean {
    return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  }

  private isProduction(): boolean {
    return window.location.protocol === 'https:' &&
           window.location.hostname !== 'localhost' &&
           window.location.hostname !== '127.0.0.1';
  }

  getApiUrl(): string {
    return this.config.apiUrl;
  }

  isDebugMode(): boolean {
    return this.config.debug ?? false;
  }

  getLogLevel(): string {
    return this.config.logLevel ?? 'warn';
  }
}
