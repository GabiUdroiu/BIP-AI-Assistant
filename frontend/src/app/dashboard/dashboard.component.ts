import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService, ColumnInfo } from '../admin.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  private adminService = inject(AdminService);

  tables = signal<string[]>([]);
  selectedTable = signal<string>('');
  columns = signal<ColumnInfo[]>([]);
  rows = signal<any[]>([]);
  formData = signal<Record<string, string>>({});
  errorMessage = signal<string>('');

  constructor() {
    this.loadTables();
  }

  loadTables() {
    this.adminService.getTables().subscribe({
      next: (res) => this.tables.set(res.data || []),
      error: () => this.errorMessage.set('Could not load tables - is backend-core running?')
    });
  }

  selectTable(table: string) {
    this.selectedTable.set(table);
    this.formData.set({});
    this.errorMessage.set('');

    this.adminService.getColumns(table).subscribe({
      next: (res) => this.columns.set(res.data || [])
    });
    this.loadRows();
  }

  loadRows() {
    if (!this.selectedTable()) return;
    this.adminService.getRows(this.selectedTable()).subscribe({
      next: (res) => this.rows.set(res.data || []),
      error: () => this.errorMessage.set('Could not load rows')
    });
  }

  updateField(column: string, value: string) {
    this.formData.update((data) => ({ ...data, [column]: value }));
  }

  submit() {
    this.errorMessage.set('');
    const data = this.formData();
    const cleaned: Record<string, string> = {};
    for (const key in data) {
      if (data[key] !== '') cleaned[key] = data[key];
    }

    this.adminService.insertRow(this.selectedTable(), cleaned).subscribe({
      next: () => {
        this.formData.set({});
        this.loadRows();
      },
      error: (err) => this.errorMessage.set(err?.error?.detail || 'Insert failed')
    });
  }

  deleteRow(row: any) {
    const pkColumn = this.columns().find((c) => c.primary_key)?.name;
    if (!pkColumn) return;

    this.adminService.deleteRow(this.selectedTable(), pkColumn, row[pkColumn]).subscribe({
      next: () => this.loadRows(),
      error: () => this.errorMessage.set('Delete failed')
    });
  }

  rowColumns(row: any): string[] {
    return Object.keys(row);
  }
}
