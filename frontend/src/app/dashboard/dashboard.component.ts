import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AdminService, ColumnInfo } from '../admin.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  private readonly adminService = inject(AdminService);

  protected readonly tables = signal<string[]>([]);
  protected readonly selectedTable = signal<string>('');
  protected readonly columns = signal<ColumnInfo[]>([]);
  protected readonly rows = signal<any[]>([]);
  protected readonly formData = signal<Record<string, string>>({});
  protected readonly errorMessage = signal<string>('');
  protected readonly editingPkValue = signal<string | null>(null);

  protected readonly pkColumn = computed(() => this.columns().find((c) => c.primary_key)?.name);

  constructor() {
    this.loadTables();
  }

  private loadTables() {
    this.adminService.getTables().subscribe({
      next: (res) => this.tables.set(res.data || []),
      error: () => this.errorMessage.set('Could not load tables - is backend-core running?')
    });
  }

  protected selectTable(table: string) {
    this.selectedTable.set(table);
    this.formData.set({});
    this.editingPkValue.set(null);
    this.errorMessage.set('');

    this.adminService.getColumns(table).subscribe({
      next: (res) => this.columns.set(res.data || [])
    });
    this.loadRows();
  }

  private loadRows() {
    if (!this.selectedTable()) return;
    this.adminService.getRows(this.selectedTable()).subscribe({
      next: (res) => this.rows.set(res.data || []),
      error: () => this.errorMessage.set('Could not load rows')
    });
  }

  protected updateField(column: string, value: string) {
    this.formData.update((data) => ({ ...data, [column]: value }));
  }

  protected startEdit(row: any) {
    const pkColumn = this.pkColumn();
    if (!pkColumn) return;

    const data: Record<string, string> = {};
    for (const key of this.rowColumns(row)) {
      data[key] = row[key] === null || row[key] === undefined ? '' : String(row[key]);
    }
    this.formData.set(data);
    this.editingPkValue.set(row[pkColumn]);
    this.errorMessage.set('');
  }

  protected cancelEdit() {
    this.formData.set({});
    this.editingPkValue.set(null);
    this.errorMessage.set('');
  }

  protected submit() {
    this.errorMessage.set('');
    const data = this.formData();
    const editingPk = this.editingPkValue();
    const pkColumn = this.pkColumn();

    if (editingPk !== null && pkColumn) {
      this.adminService.updateRow(this.selectedTable(), pkColumn, editingPk, data).subscribe({
        next: () => {
          this.cancelEdit();
          this.loadRows();
        },
        error: (err) => this.errorMessage.set(err?.error?.detail || 'Update failed')
      });
      return;
    }

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

  protected deleteRow(row: any) {
    const pkColumn = this.pkColumn();
    if (!pkColumn) return;

    this.adminService.deleteRow(this.selectedTable(), pkColumn, row[pkColumn]).subscribe({
      next: () => this.loadRows(),
      error: () => this.errorMessage.set('Delete failed')
    });
  }

  protected rowColumns(row: any): string[] {
    return Object.keys(row);
  }
}
