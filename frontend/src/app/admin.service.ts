import { Injectable } from '@angular/core';
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
  private apiUrl = 'http://localhost:8080/api/admin';

  constructor(private http: HttpClient) {}

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

  deleteRow(table: string, pkColumn: string, pkValue: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/tables/${table}/rows/${pkColumn}/${pkValue}`);
  }
}
