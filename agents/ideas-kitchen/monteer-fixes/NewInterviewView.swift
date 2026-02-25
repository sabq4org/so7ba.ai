// MARK: - NewInterviewView (محسّن)
// التحسينات:
// 1. الحقول محاذاة يمين مع labels فوق كل حقل
// 2. زر الإلغاء في المكان الصحيح
// 3. حقل إضافي لاسم الصحفي
// 4. النجمة * بعد النص العربي
// 5. الزر فعّال فقط لما تتملأ الحقول الإلزامية
// 6. تصميم بصري أوضح وأكثر هواء

import SwiftUI

struct NewInterviewView: View {
    @Environment(\.dismiss) var dismiss

    @State private var title: String = ""
    @State private var guestName: String = ""
    @State private var journalistName: String = ""
    @State private var position: String = ""
    @State private var topic: String = ""

    var isFormValid: Bool {
        !title.trimmingCharacters(in: .whitespaces).isEmpty &&
        !guestName.trimmingCharacters(in: .whitespaces).isEmpty
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {

                    // ── قسم: تفاصيل المقابلة ──
                    VStack(alignment: .trailing, spacing: 0) {
                        SectionHeader(title: "تفاصيل المقابلة")

                        VStack(spacing: 0) {
                            RTLField(
                                label: "عنوان المقابلة",
                                placeholder: "مثال: حوار حول الذكاء الاصطناعي",
                                text: $title,
                                isRequired: true
                            )
                            Divider().padding(.horizontal)
                            RTLField(
                                label: "اسم الضيف",
                                placeholder: "الاسم الكامل للضيف",
                                text: $guestName,
                                isRequired: true
                            )
                            Divider().padding(.horizontal)
                            RTLField(
                                label: "المنصب / الصفة",
                                placeholder: "مثال: وزير، مدير عام، أكاديمي...",
                                text: $position,
                                isRequired: false
                            )
                        }
                        .background(Color(.systemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                    }

                    // ── قسم: بيانات المحاور ──
                    VStack(alignment: .trailing, spacing: 0) {
                        SectionHeader(title: "بيانات المحاور")

                        VStack(spacing: 0) {
                            RTLField(
                                label: "اسم الصحفي / المحاور",
                                placeholder: "اسمك أو اسم من يُجري المقابلة",
                                text: $journalistName,
                                isRequired: false
                            )
                            Divider().padding(.horizontal)
                            RTLField(
                                label: "الموضوع / الملف",
                                placeholder: "الموضوع الرئيسي للمقابلة",
                                text: $topic,
                                isRequired: false
                            )
                        }
                        .background(Color(.systemBackground))
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                    }

                    // ── ملاحظة الحقول الإلزامية ──
                    HStack {
                        Spacer()
                        Text("* الحقول الإلزامية")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal, 4)

                    // ── زر ابدأ التسجيل ──
                    Button {
                        // action: start recording
                    } label: {
                        HStack(spacing: 10) {
                            Image(systemName: "mic.fill")
                                .font(.body)
                            Text("ابدأ التسجيل")
                                .font(.body)
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(isFormValid ? Color.red : Color(.systemGray4))
                        .foregroundColor(isFormValid ? .white : Color(.systemGray2))
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                    }
                    .disabled(!isFormValid)
                    .animation(.easeInOut(duration: 0.2), value: isFormValid)

                    Spacer(minLength: 40)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("مقابلة جديدة")
            .navigationBarTitleDisplayMode(.inline)
            .environment(\.layoutDirection, .rightToLeft)
            .toolbar {
                // الإلغاء — يمين (trailing في RTL = الجهة اليمنى)
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("إلغاء") {
                        dismiss()
                    }
                    .foregroundColor(.red)
                }
            }
        }
        .environment(\.layoutDirection, .rightToLeft)
    }
}

// MARK: - مكوّن: عنوان القسم
struct SectionHeader: View {
    let title: String
    var body: some View {
        Text(title)
            .font(.footnote)
            .fontWeight(.medium)
            .foregroundColor(.secondary)
            .frame(maxWidth: .infinity, alignment: .trailing)
            .padding(.bottom, 8)
            .padding(.horizontal, 4)
    }
}

// MARK: - مكوّن: حقل نص RTL مع label
struct RTLField: View {
    let label: String
    let placeholder: String
    @Binding var text: String
    let isRequired: Bool

    var body: some View {
        VStack(alignment: .trailing, spacing: 4) {
            // Label
            HStack(spacing: 2) {
                if isRequired {
                    Text("*")
                        .font(.caption)
                        .foregroundColor(.red)
                }
                Text(label)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
            }

            // TextField
            TextField(placeholder, text: $text)
                .multilineTextAlignment(.trailing)
                .font(.body)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
    }
}

// MARK: - Preview
#Preview {
    NewInterviewView()
}
