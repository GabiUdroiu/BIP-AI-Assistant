import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EnvironmentService } from './environment.service';
import { ApiResponse, ColumnInfo } from './models/api-response';
import { CacheFactory } from './utils/cache-factory';

// Re-export for components using this service
export type { ColumnInfo };

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly http = inject(HttpClient);
  private readonly env = inject(EnvironmentService);

  private tablesCache = new Map<string, string[] | null>();
  private columnsCache = new Map<string, ColumnInfo[] | null>();
  private rowsCache = new Map<string, any[] | null>();

  private get apiUrl(): string {
    return this.env.getApiUrl();
  }

  getTables(): Observable<ApiResponse<string[]>> {
    return CacheFactory.cached(
      this.tablesCache,
      'tables',
      () => this.http.get<ApiResponse<string[]>>(`${this.apiUrl}/admin/tables`)
    );
  }

  getColumns(table: string): Observable<ApiResponse<ColumnInfo[]>> {
    return CacheFactory.cached(
      this.columnsCache,
      `columns:${table}`,
      () => this.http.get<ApiResponse<ColumnInfo[]>>(`${this.apiUrl}/admin/tables/${table}/columns`)
    );
  }

  getRows(table: string): Observable<ApiResponse<any[]>> {
    return CacheFactory.cached(
      this.rowsCache,
      `rows:${table}`,
      () => this.http.get<ApiResponse<any[]>>(`${this.apiUrl}/admin/tables/${table}/rows`)
    );
  }

  insertRow(table: string, data: Record<string, string>): Observable<ApiResponse<any>> {
    return new Observable((obs) => {
      this.http
        .post<ApiResponse<any>>(`${this.apiUrl}/admin/tables/${table}/rows`, { data })
        .subscribe({
          next: (res) => {
            CacheFactory.invalidate(this.rowsCache, `rows:${table}`);
            obs.next(res);
            obs.complete();
          },
          error: (err) => obs.error(err),
        });
    });
  }

  updateRow(
    table: string,
    pkColumn: string,
    pkValue: string,
    data: Record<string, string>
  ): Observable<ApiResponse<any>> {
    return new Observable((obs) => {
      this.http
        .patch<ApiResponse<any>>(
          `${this.apiUrl}/admin/tables/${table}/rows/${pkColumn}/${pkValue}`,
          { data }
        )
        .subscribe({
          next: (res) => {
            CacheFactory.invalidate(this.rowsCache, `rows:${table}`);
            obs.next(res);
            obs.complete();
          },
          error: (err) => obs.error(err),
        });
    });
  }

  deleteRow(table: string, pkColumn: string, pkValue: string): Observable<ApiResponse<any>> {
    return new Observable((obs) => {
      this.http
        .delete<ApiResponse<any>>(`${this.apiUrl}/admin/tables/${table}/rows/${pkColumn}/${pkValue}`)
        .subscribe({
          next: (res) => {
            CacheFactory.invalidate(this.rowsCache, `rows:${table}`);
            obs.next(res);
            obs.complete();
          },
          error: (err) => obs.error(err),
        });
    });
  }

  clearCache(table?: string): void {
    if (table) {
      CacheFactory.invalidate(this.rowsCache, `rows:${table}`);
      CacheFactory.invalidate(this.columnsCache, `columns:${table}`);
    } else {
      CacheFactory.invalidate(this.tablesCache);
      CacheFactory.invalidate(this.rowsCache);
      CacheFactory.invalidate(this.columnsCache);
    }
  }
}
