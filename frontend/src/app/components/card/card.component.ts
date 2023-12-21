<!-- pages/home/home.component.html -->
<button mat-raised-button color="primary" (click)="toogleHomeLogin()">Switch Login/Home</button>

<div class="accessibility" *ngIf="showHome" >Access
  


<app-registration *ngIf="showLogin"></app-registration>
  <app-login *ngIf="!showLogin"></app-login>
   
  <button mat-raised-button color="primary" (click)="toggleLoginRegistration()">Switch Form</button>
</div>


<!-- home.component.html -->


<div class="main-content"  *ngIf="!showHome">
  <div class="card-container" style="--images-per-row: {{ imagesPerRow }}">
    <app-card *ngFor="let imageUrl of imageUrls" [imageUrls]="[imageUrl]"></app-card>
  </div>
</div>







