import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8080/api/admin';

  getTables(): Observable<any> {
    return this.http.get(`${this.apiUrl}/tables`);
  }

  getColumns(table: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/tables/${table}/columns`);
  }

  getRows(table: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/tables/${table}/rows`);
  }

  insertRow(table: string, data: Record<string, string>): Observable<any> {
    return this.http.post(`${this.apiUrl}/tables/${table}/rows`, { data });
  }

  updateRow(table: string, pkColumn: string, pkValue: string, data: Record<string, string>): Observable<any> {
    return this.http.patch(`${this.apiUrl}/tables/${table}/rows/${pkColumn}/${pkValue}`, { data });
  }

  deleteRow(table: string, pkColumn: string, pkValue: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/tables/${table}/rows/${pkColumn}/${pkValue}`);
  }
}
