import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { InvoiceService } from '../../services/invoice.service';
import { Invoice } from '../../models/invoice.model';

@Component({
  selector: 'app-invoice-list',
  templateUrl: './invoice-list.component.html',
  styleUrls: ['./invoice-list.component.scss']
})
export class InvoiceListComponent implements OnInit {
  displayedColumns: string[] = ['invoice_number', 'supplier_name', 'invoice_date', 'total_amount', 'status', 'confidence_score', 'actions'];
  dataSource = new MatTableDataSource<Invoice>([]);
  isLoading = true;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private invoiceService: InvoiceService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadInvoices();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadInvoices(): void {
    this.isLoading = true;
    this.invoiceService.getInvoices().subscribe({
      next: (invoices) => {
        this.dataSource.data = invoices;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des factures:', error);
        this.isLoading = false;
      }
    });
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  viewInvoice(id: number): void {
    this.router.navigate(['/invoices', id]);
  }

  editInvoice(id: number): void {
    this.router.navigate(['/invoices', id, 'edit']);
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'validated':
        return 'status-validated';
      case 'processed':
        return 'status-processed';
      case 'error':
        return 'status-error';
      default:
        return 'status-pending';
    }
  }

  getStatusLabel(status: string): string {
    switch (status) {
      case 'pending':
        return 'En attente';
      case 'processing':
        return 'En cours';
      case 'processed':
        return 'Traitée';
      case 'error':
        return 'Erreur';
      case 'validated':
        return 'Validée';
      default:
        return status;
    }
  }

  getConfidenceColor(score: number): string {
    if (score >= 0.8) return 'green';
    if (score >= 0.5) return 'orange';
    return 'red';
  }
}