import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './components/header/header.component';
import { FooterComponent } from './components/footer/footer.component';
import { SharedComponent } from './components/shared/shared.component';
import { RegistrationComponent } from './components/registration/registration.component';
import { LoginComponent } from './components/login/login.component';
import { HomeComponent } from './pages/home/home/home.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
// Aggiungi le seguenti importazioni per Angular Material
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import {MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
//
import { SearchBarComponent } from './components/search-bar/search-bar.component';
import { AboutComponent } from './pages/about/about/about.component';
import { ErrorComponent } from './pages/error/error/error.component';
import { KartComponent } from './pages/kart/kart/kart.component';
import { PayComponent } from './pages/pay/pay/pay.component';
import { ProductComponent } from './pages/product/product/product.component';
import { ProfileComponent } from './pages/profile/profile/profile.component';
import { UserManagementComponent } from './pages/user_management/user-management/user-management.component';
import { ContactComponent } from './pages/contact/contact/contact.component';
import { CardComponent } from './components/card/card.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    FooterComponent,
    SharedComponent,
    RegistrationComponent,
    LoginComponent,
    HomeComponent,
    SearchBarComponent,
    AboutComponent,
    ErrorComponent,
    KartComponent,
    PayComponent,
    ProductComponent,
    ProfileComponent,
    UserManagementComponent,
    ContactComponent,
    CardComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatToolbarModule,
    MatIconModule,
    MatCardModule
    
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
