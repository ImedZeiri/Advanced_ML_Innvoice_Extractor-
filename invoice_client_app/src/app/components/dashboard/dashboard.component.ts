import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { InvoiceService } from '../../services/invoice.service';
import { ModelStats } from '../../models/invoice.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  modelStats: ModelStats | null = null;
  isLoading = true;
  errorMessage = '';
  
  constructor(
    private invoiceService: InvoiceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadModelStats();
  }

  loadModelStats(): void {
    this.isLoading = true;
    this.invoiceService.getModelStats().subscribe({
      next: (stats) => {
        this.modelStats = stats;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Impossible de charger les statistiques du modèle';
        this.isLoading = false;
        console.error('Error loading model stats:', error);
      }
    });
  }

  uploadNewInvoice(): void {
    this.router.navigate(['/']);
  }
}