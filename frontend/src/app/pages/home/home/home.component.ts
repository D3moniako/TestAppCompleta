// pages/home/home.component.ts

import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  constructor(private router: Router) {}

  // Metodo per cambiare la rotta
  navigateToOtherPage() {
    this.router.navigate(['/altro-percorso']);
  }

  showLogin: boolean = true;
  showHome: boolean = true;


  toggleLoginRegistration() {
    this.showLogin = !this.showLogin;
  }

  toogleHomeLogin(){
    this.showHome = !this.showHome;
  }
  // Definiamo il numero di elementi per riga
  imagesPerRow: number = 1;

  // GESTIONE IMMAGINI CARD 
  imageUrls: string[] = [
    'assets/images/photo (1).jpg',
    'assets/images/photo (10).jpg',
    'assets/images/photo (11).jpg',
    'assets/images/photo (12).jpg',
    'assets/images/photo (13).jpg',
     
    'assets/images/photo (14).jpg',
    // 'assets/images/photo (15).jpg',
    // 'assets/images/photo (16).jpg',
    // ... altre URL delle immagini
  ];
  
}

