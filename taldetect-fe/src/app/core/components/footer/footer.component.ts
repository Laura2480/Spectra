import { Component, Output, EventEmitter } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [MatIconModule, TranslateModule],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.scss'
})
export class FooterComponent {
  @Output() switchLanguage: EventEmitter<string> = new EventEmitter<string>();

  sendSwitchLanguage(lang: string) {
    this.switchLanguage.emit(lang)
  }
}
