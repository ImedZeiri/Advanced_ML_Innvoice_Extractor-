import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { Invoice } from '../../models/invoice.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  recentInvoices: Invoice[] = [];
  isLoading = true;
  stats = {
    total: 0,
    validated: 0,
    pending: 0,
    error: 0,
    averageConfidence: 0
  };

  constructor(
    private invoiceService: InvoiceService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadInvoices();
  }

  loadInvoices(): void {
    this.isLoading = true;
    this.invoiceService.getInvoices().subscribe({
      next: (invoices) => {
        this.recentInvoices = invoices.slice(0, 5);
        this.calculateStats(invoices);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur lors du chargement des factures:', error);
        this.isLoading = false;
      }
    });
  }

  calculateStats(invoices: Invoice[]): void {
    this.stats.total = invoices.length;
    this.stats.validated = invoices.filter(i => i.status === 'validated').length;
    this.stats.pending = invoices.filter(i => i.status === 'pending' || i.status === 'processing').length;
    this.stats.error = invoices.filter(i => i.status === 'error').length;
    
    // Calcul du score de confiance moyen
    if (invoices.length > 0) {
      const totalConfidence = invoices.reduce((sum, invoice) => sum + invoice.confidence_score, 0);
      this.stats.averageConfidence = totalConfidence / invoices.length;
    }
  }

  trainModel(): void {
    this.invoiceService.trainModel().subscribe({
      next: (response) => {
        console.log('Modèle entraîné avec succès:', response);
        // Afficher une notification de succès
      },
      error: (error) => {
        console.error('Erreur lors de l\'entraînement du modèle:', error);
        // Afficher une notification d'erreur
      }
    });
  }

  navigateToInvoices(): void {
    this.router.navigate(['/invoices']);
  }

  navigateToUpload(): void {
    this.router.navigate(['/invoices/upload']);
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
}