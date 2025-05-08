import { Component } from '@angular/core';
import {
  FormGroup,
  ReactiveFormsModule,
  FormControl,
  FormBuilder,
  Validators,
} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { TranslateModule } from '@ngx-translate/core';
import { UserService } from '../login/services/user.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-create-user',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    TranslateModule,
  ],
  templateUrl: './create-user.component.html',
  styleUrl: './create-user.component.scss',
})
export class CreateUserComponent {
  userRegistrationForm: FormGroup;

  constructor(private fb: FormBuilder, private userService: UserService, private toastr: ToastrService) {
    this.userRegistrationForm = this.fb.group({
      nome: ['', Validators.required],
      cognome: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
    });
  }

  onSubmit() {
    if (this.userRegistrationForm.valid) {
      const userData = this.userRegistrationForm.value;

      this.userService.registerUser(userData).subscribe({
        next: (response) => {
          console.log('Registrazione avvenuta con successo:', response);
          this.toastr.success('Utente registrato con successo!', 'Successo');
          this.userRegistrationForm.reset();
        },
        error: (error) => {
          console.error('Errore durante la registrazione:', error);
          this.toastr.error('Errore nella registrazione, riprova.', 'Errore');
        },
      });
    } else {
      this.toastr.error('Compila tutti i campi correttamente.', 'Errore');
    }
  }
}
